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
        username = filename.split(".")[0]
        # With co-authors
        # if username not in (
        #     "ahernn",
        #     "falsafin",
        #     "mechlingb",
        #     "waldschlagelm",
        #     "devitaj",
        #     "kolomers",
        #     "palumbor",
        #     "leej",
        # ):
        #     continue
        # With PERFORM_EXHIBITs
        # if username not in (
        #     "cordied",
        #     "cordiep",
        #     "degennarod",
        #     "errantes",
        #     "furiap",
        #     "haddadl",
        #     "kaylorj",
        #     "kingn",
        # ):
        # continue
        # With INTELLPROP
        # if username not in ("baden", "carrm", "changy"):
        #     continue
        # debugging why dates aren't sticking
        # if username not in (
        #     "mcbrayerl",
        #     "carrm",
        # ):
        # WITH CONGRANT
        if username not in ("sackleyw", "covij"):
            continue
        # if username in preignored_users:
        #     continue
        filepath = os.path.join(USERFILES_DIR, filename)
        parsed_user = parse_userfile(filepath)
        if is_excluded_user(parsed_user, driver):
            continue
        add_user_to_graph(parsed_user, graph)
    driver.close()
    return graph


def write_turtle(graph):
    filetext = graph.serialize(format="turtle").decode("utf-8")
    os.makedirs("output", exist_ok=True)
    with open(f"output/vivo_import_{datetime.now().timestamp()}.ttl", "w") as f:
        f.write(filetext)


if __name__ == "__main__":
    # scrape_digitalmeasures()
    graph = make_graph()
    # write_turtle(graph)
