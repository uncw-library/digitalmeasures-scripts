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
PARSED_USERS_DIR = os.path.join("output", "parsed_users")
PERSON_IMAGES_DIR = os.path.join("output", "person_images")
TURTLES_DIR = os.path.join("output", "turtles")


def hard_refresh(USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR, PARSED_USERS_DIR):
    for folder in (USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR, PARSED_USERS_DIR):
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder, exist_ok=True)


def scrape_digitalmeasures(dm_user, dm_pass):
    creds = {"user": dm_user, "password": dm_pass}
    usernames = scrape_userrecords.get_usernames(creds)
    scrape_userrecords.do_userfiles(usernames, creds, USERFILES_DIR)


def write_turtle(graph):
    filetext = graph.serialize(format="turtle").decode("utf-8")

    os.makedirs(TURTLES_DIR, exist_ok=True)
    turtle_files = [os.path.join(TURTLES_DIR, i) for i in os.listdir(TURTLES_DIR)]
    for i in turtle_files:
        os.remove(i)
    with open(os.path.join(TURTLES_DIR, "userdata.ttl"), "w") as f:
        f.write(filetext)


if __name__ == "__main__":
    dm_user, dm_pass = os.getenv("DMUSER"), os.getenv("DMPASS")
    if not (dm_user and dm_pass):
        print("please create a file .env with DMUSER and DMPASS")
    # hard_refresh(USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR, PARSED_USERS_DIR)
    scrape_digitalmeasures(dm_user, dm_pass)
    scrape_profile_images(USERFILES_DIR, PERSON_IMAGES_DIR)
    parse_and_pretty_print(USERFILES_DIR, PARSED_USERS_DIR)
    split_include_exclude(USERFILES_DIR, INCLUDE_DIR, EXCLUDE_DIR)
    graph = make_graph(INCLUDE_DIR)
    write_turtle(graph)
