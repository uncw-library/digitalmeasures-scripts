#!/usr/bin/env python
# xml_to_turtle.py

import os
import getpass
import shutil
from datetime import datetime

import scrape_userrecords
from parse_userfiles import parse_and_pretty_print
from exclude_users import split_include_exclude
from graph_builder.make_graph import make_graph
from scrape_profile_images import scrape_profile_images

USERFILES_DIR = os.path.join("output", "users")
INCLUDE_DIR = os.path.join("output", "included_users")
EXCLUDE_DIR = os.path.join("output", "excluded_users")
TEST_PARSED_USERS = os.path.join("output", "test_parsed_users")
PERSON_IMAGES_DIR = os.path.join("output", "person_images")


def hard_refresh(USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR):
    for folder in (USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR, TEST_PARSED_USERS):
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder, exist_ok=True)


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
    hard_refresh(USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR)
    scrape_digitalmeasures()
    scrape_profile_images(USERFILES_DIR, PERSON_IMAGES_DIR)
    parse_and_pretty_print(USERFILES_DIR, TEST_PARSED_USERS)
    split_include_exclude(USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR)
    graph = make_graph(INCLUDE_DIR)
    write_turtle(graph)
