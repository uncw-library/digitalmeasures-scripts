#!/usr/bin/env python
# xml_to_turtle.py

import os
from datetime import datetime
import getpass

from exclude_users import preignored_users, is_excluded_user
from make_turtle import init_graph, add_orgs_to_graph, add_user_to_graph
from parse_userfiles import parse_userfile
from scrape_directory import driver
import scrape_userrecords


USERFILES_DIR = os.path.join("output", "users")


def scrape_digitalmeasures():
    creds = {"user": "uncw/web_services_vivo", "password": getpass.getpass()}
    usernames = scrape_userrecords.get_usernames(creds)
    scrape_userrecords.do_userfiles(usernames, creds, USERFILES_DIR)


def make_graph():
    graph = init_graph()
    add_orgs_to_graph(graph)

    for filename in sorted(os.listdir(USERFILES_DIR)):
        filepath = os.path.join(USERFILES_DIR, filename)
        username = filename.split(".")[0]
        if not include_while_developing(username):
            continue
        if username in preignored_users:
            continue
        parsed_user = parse_userfile(filepath)
        if is_excluded_user(parsed_user, driver):
            continue
        add_user_to_graph(graph, parsed_user)
    driver.close()
    return graph


def write_turtle(graph):
    filetext = graph.serialize(format="turtle").decode("utf-8")
    os.makedirs("output", exist_ok=True)
    with open(f"output/vivo_import_{datetime.now().timestamp()}.ttl", "w") as f:
        f.write(filetext)


def include_while_developing(username):
    # if has_coauthor(username):
    #     return True
    # if has_PERFORM_EXHIBIT(username):
    #     return True
    # if has_INTELLPROP(username):
    #     return True
    if has_CONGRANT(username):
        return True
    # if has_BIO(username):
    #     return True
    # if has_active_ADMIN_ASSIGNMENTS(username):
    #     return True
    # if has_mismatched_titles(username):
    #     return True
    return False


def has_coauthor(username):
    # With co-authors
    if username in (
        "ahernn",
        "falsafin",
        "mechlingb",
        "waldschlagelm",
        "devitaj",
        "kolomers",
        "palumbor",
        "leej",
    ):
        return True
    return False


def has_PERFORM_EXHIBIT(username):
    if username in (
        "cordied",
        "cordiep",
        "degennarod",
        "errantes",
        "furiap",
        "haddadl",
        "kaylorj",
        "kingn",
    ):
        return True
    return False


def has_INTELLPROP(username):
    if username in ("baden", "carrm", "changy"):
        return True
    return False


def has_CONGRANT(username):
    if username in ("turrises", "bovel", "carrollr"):
        return True
    return False


def has_BIO(username):
    if username in ("struckelle",):
        return True
    return False


def has_mismatched_titles(username):
    if username in ("schnorrc", "andrewsm", "bergh", "biehnerb"):
        return True
    return False


def has_active_ADMIN_ASSIGNMENTS(username):
    if username in ("ahernn", "chandlerb", "cathorallm", "calhound", "buffingtond"):
        return True
    return False


if __name__ == "__main__":
    # scrape_digitalmeasures()
    graph = make_graph()
    write_turtle(graph)
