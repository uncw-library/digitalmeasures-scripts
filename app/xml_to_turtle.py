#!/usr/bin/env python
# xml_to_turtle.py

import os
from datetime import datetime
import getpass
import json
import pprint

from exclude_users import preignored_users, is_excluded_user
from make_turtle import init_graph, add_user_to_graph
from add_orgs import add_orgs_to_graph
from parse_userfiles import parse_userfile
from scrape_directory import driver
import scrape_userrecords

import include_while_developing

from make_turtle import conjure_coll_dept_assignment

USERFILES_DIR = os.path.join("output", "users")


def scrape_digitalmeasures():
    creds = {"user": "uncw/web_services_vivo", "password": getpass.getpass()}
    usernames = scrape_userrecords.get_usernames(creds)
    scrape_userrecords.do_userfiles(usernames, creds, USERFILES_DIR)


def hack_move_non_selected_from_source_folder():
    EXCLUDE_DIR = os.path.join("output", "excluded_users")
    os.makedirs(EXCLUDE_DIR, exist_ok=True)
    for filename in sorted(os.listdir(USERFILES_DIR)):
        username = filename.split(".")[0]
        print(username)

        if username in preignored_users:
            os.rename(
                os.path.join(USERFILES_DIR, filename),
                os.path.join(EXCLUDE_DIR, filename),
            )
            continue

        filepath = os.path.join(USERFILES_DIR, filename)
        parsed_user = parse_userfile(filepath)
        if is_excluded_user(parsed_user, driver):
            os.rename(
                os.path.join(USERFILES_DIR, filename),
                os.path.join(EXCLUDE_DIR, filename),
            )
            continue

        dept = parsed_user.get("current_depts")
        likely_coll_dept = conjure_coll_dept_assignment(parsed_user)

        if not likely_coll_dept:
            os.rename(
                os.path.join(USERFILES_DIR, filename),
                os.path.join(EXCLUDE_DIR, filename),
            )
            continue

        exclude = True
        for i in likely_coll_dept:
            if i["coll_name"] == "College of Health and Human Services":
                exclude = False
            if i["dept_name"] == "Randall Library":
                exclude = False
        if exclude:
            os.rename(
                os.path.join(USERFILES_DIR, filename),
                os.path.join(EXCLUDE_DIR, filename),
            )
            continue


def make_graph():
    graph = init_graph()
    add_orgs_to_graph(graph)

    for filename in sorted(os.listdir(USERFILES_DIR)):
        filepath = os.path.join(USERFILES_DIR, filename)
        username = filename.split(".")[0]
        # if not include_while_developing(username):
        #     continue
        if username in preignored_users:
            continue
        parsed_user = parse_userfile(filepath)
        # pretty printing parsed_user
        with open(f"test_parsed_users/{os.path.splitext(filename)[0]}.txt", 'w') as f:
            prettytext = pprint.pformat(parsed_user, width=120, sort_dicts=False)
            f.write(prettytext)
        if is_excluded_user(parsed_user, driver):
            continue
        # add_user_to_graph(graph, parsed_user)
    driver.close()
    return graph

def write_turtle(graph):
    filetext = graph.serialize(format="turtle").decode("utf-8")
    os.makedirs("output", exist_ok=True)
    with open(f"output/vivo_import_{datetime.now().timestamp()}.ttl", "w") as f:
        f.write(filetext)


if __name__ == "__main__":
    # scrape_digitalmeasures()
    # hack_move_non_selected_from_source_folder()
    graph = make_graph()
    # write_turtle(graph)
