#!/usr/bin/env python3
# xml_to_turtle.py

import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
import logging

import scrape_userrecords
from parse_userfiles import parse_and_pretty_print
from exclude_users import remove_excluded_users
from graph_builder.make_graph import make_graph
from scrape_profile_images import scrape_profile_images
from utils import setup_logging, parse_args
from dbs.joblog import update_joblog 


APP_ROOT = os.path.split(os.path.realpath(__file__))[0]
OUTPUT_ROOT = os.path.join(APP_ROOT, "..", "output")
USERFILES_DIR = os.path.join(OUTPUT_ROOT, "users")
PARSED_USERS_DIR = os.path.join(OUTPUT_ROOT, "parsed_users")
PERSON_IMAGES_DIR = os.path.join(OUTPUT_ROOT, "person_images")
TURTLES_DIR = os.path.join(OUTPUT_ROOT, "turtles")


# removes the source data, so new data can be pulled.
# --no_reset flag will skip this slow step
def hard_reset(USERFILES_DIR, PARSED_USERS_DIR):
    for folder in (USERFILES_DIR, PARSED_USERS_DIR):
        shutil.rmtree(folder, ignore_errors=True)


def make_output_dirs(USERFILES_DIR, PARSED_USERS_DIR, PERSON_IMAGES_DIR, TURTLES_DIR):
    for folder in (USERFILES_DIR, PARSED_USERS_DIR, PERSON_IMAGES_DIR, TURTLES_DIR):
        os.makedirs(folder, exist_ok=True)
    logging.info("output folders created")


def scrape_digitalmeasures(dm_user, dm_pass):
    creds = {"user": dm_user, "password": dm_pass}
    usernames = scrape_userrecords.get_usernames(creds)
    scrape_userrecords.do_userfiles(usernames, creds, USERFILES_DIR)
    logging.info("scrape digitalmeasures complete")


def write_turtle(TURTLES_DIR, graph):
    filetext = graph.serialize(format="turtle")
    if type(filetext) != str:
        filetext = filetext.decode("utf-8")
    now = datetime.now().timestamp()
    now_file = os.path.join(TURTLES_DIR, f"vivo_import_{now}.ttl")
    with open(now_file, "w") as f:
        f.write(filetext)
    logging.info(f"New turtle written to {now_file}")

    latest = os.path.join(TURTLES_DIR, "userdata.ttl")
    shutil.copy2(now_file, latest)
    logging.info(f"latest version copied to {latest}")


def remove_old_turtles(TURTLES_DIR):
    turtles = [
        os.path.join(root, file)
        for root, dirs, files in os.walk(TURTLES_DIR)
        for file in files
        if file != "userdata.ttl"
    ]
    # exclude most recent one, then delete the rest
    for_deletion = sorted(turtles)
    for_deletion.pop()
    for filepath in for_deletion:
        os.remove(filepath)
    logging.info(f"deleted old turtle files: {for_deletion}")


def main_loop(flags):
    dm_user, dm_pass = os.getenv("DM_API_USER"), os.getenv("DM_API_PASS")
    if not (dm_user and dm_pass):
        logging.warning("")
        logging.warning("please create a file .env with DMUSER= and DMPASS=")
        logging.warning("")
        exit()

    if not "no_reset" in flags:
        hard_reset(USERFILES_DIR, PARSED_USERS_DIR)
        logging.info("hard reset complete")
    else:
        logging.info("skipping hard refresh of dm data")

    make_output_dirs(USERFILES_DIR, PARSED_USERS_DIR, TURTLES_DIR, PERSON_IMAGES_DIR)
    scrape_digitalmeasures(dm_user, dm_pass)
    parse_and_pretty_print(USERFILES_DIR, PARSED_USERS_DIR)
    remove_excluded_users(PARSED_USERS_DIR)
    scrape_profile_images(PARSED_USERS_DIR, PERSON_IMAGES_DIR)
    graph = make_graph(PARSED_USERS_DIR)
    write_turtle(TURTLES_DIR, graph)
    remove_old_turtles(TURTLES_DIR)
    update_joblog()


if __name__ == "__main__":
    setup_logging(APP_ROOT)
    flags = parse_args()
    load_dotenv()
    try:
        main_loop(flags)
    except Exception:
        logging.warning("Uncaught fatal error", exc_info=True)
