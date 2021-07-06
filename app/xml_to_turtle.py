#!/usr/bin/env python
# xml_to_turtle.py

import os
import getpass
from datetime import datetime

import scrape_userrecords
from parse_userfiles import parse_and_pretty_print
from exclude_users import split_include_exclude
from graph_builder.make_graph import make_graph

USERFILES_DIR = os.path.join("output", "users")


def scrape_digitalmeasures():
    creds = {"user": "uncw/web_services_vivo", "password": getpass.getpass()}
    usernames = scrape_userrecords.get_usernames(creds)
    scrape_userrecords.do_userfiles(usernames, creds, USERFILES_DIR)


def write_turtle(graph):
    filetext = graph.serialize(format="turtle").decode("utf-8")
    os.makedirs("output/turtles", exist_ok=True)
    with open(f"output/turtles/vivo_import_{datetime.now().timestamp()}.ttl", "w") as f:
        f.write(filetext)


if __name__ == "__main__":
    # scrape_digitalmeasures()
    # parse_and_pretty_print(USERFILES_DIR)
    include_dir, exclude_dir = split_include_exclude(USERFILES_DIR)
    graph = make_graph(include_dir)
    write_turtle(graph)
