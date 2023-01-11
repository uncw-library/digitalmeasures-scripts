# exclude_users.py

import json
import logging
import os

from scrape_directory import SeleniumDriver
from graph_builder.make_graph import conjure_coll_dept_assignment


GENERIC_USERS = {"facultytest"}
IRP = {"morristr"}
OFFICE_STAFF = {
    "armstrongg",
    "baileyj",
    "beaudoinh",
    "deltsi",
    "depompeisd",
    "grays",
    "hartmanc",
    "lindgrens",
    "mcdanielk",
    "murrayd",
    "ramadanik",
    "wrightlk",
    "helmsc",
    "smithzr",
}
NONFAC = {"sartarellij", "powells", "tirrelld", "ndoyea", "winebrakej"}
OTHER_BAD_DATA = {"battenk"}
FORCE_EXCLUDE = set().union(GENERIC_USERS, OFFICE_STAFF, IRP, NONFAC, OTHER_BAD_DATA)

FORCE_INCLUDE = {"crowes", "fritzlerp", "saundersn"}


def remove_excluded_users(parsed_users_dir):
    selenium_driver = SeleniumDriver()
    all_filenames = sorted(os.listdir(parsed_users_dir))
    for filename in all_filenames:
        if is_exclude(parsed_users_dir, filename, selenium_driver):
            os.remove(os.path.join(parsed_users_dir, filename))
            print(f"removed {filename}")
    selenium_driver.driver.quit()
    logging.info("removed excluded users from parsed_users dir")


def is_exclude(parsed_users_dir, filename, selenium_driver):
    filepath = os.path.join(parsed_users_dir, filename)
    with open(filepath, "r") as f:
        parsed_user = json.load(f)

    if not parsed_user:
        return True
    if is_force_include(parsed_user):
        return False
    if is_force_exclude(parsed_user):
        return True
    if is_only_do_not_use(parsed_user):
        return True
    if is_student(parsed_user):
        return True
    if is_in_excluded_dept(parsed_user):
        return True
    if not is_in_directory(parsed_user, selenium_driver):
        return True

    return False


def is_force_include(parsed_user):
    if parsed_user.get("username") in FORCE_INCLUDE:
        return True
    return False


def is_force_exclude(parsed_user):
    if parsed_user.get("username") in FORCE_EXCLUDE:
        return True
    return False


def is_only_do_not_use(parsed_user):
    # some users have a department name with the text "DO NOT USE".
    # exclude the user if all their departments names are such.
    listed_depts = [dept for dept in parsed_user.get("current_depts") if dept]
    minus_do_not_use_depts = [
        dept
        for dept in parsed_user.get("current_depts")
        if dept and "do not use" not in dept.lower()
    ]
    if len(listed_depts) != len(minus_do_not_use_depts):
        return True
    return False


def is_student(parsed_user):
    username = parsed_user.get("username")
    if username[-4:].isnumeric():
        return True
    return False


def is_in_excluded_dept(parsed_user):
    likely_coll_dept = conjure_coll_dept_assignment(parsed_user)
    if not likely_coll_dept:
        return True

    # each user may have multiple likely_coll_dept.
    # loop through them all, and make exclude == False if any match.
    exclude = True
    included_colls = (
        "Cameron School of Business",
        "College of Arts and Sciences",
        "College of Health and Human Services",
        "Watson College of Education",

    )
    for i in likely_coll_dept:
        if i["coll_name"] in included_colls:
            exclude = False
        if i["dept_name"] == "Randall Library":
            exclude = False
    if exclude:
        return True

    return False


def is_in_directory(parsed_user, selenium_driver):
    # directory requires each namepart have 2+ characters.
    # someone with short lastname can't be found.
    # same for some one with short firstname.
    # Erring on the side of including those with short names.

    try:
        firstname = parsed_user.get("person").get("firstname")
    except AttributeError:
        firstname = None
    if not firstname or len(firstname) < 2:
        return True

    try:
        lastname = parsed_user.get("person").get("lastname")
    except AttributeError:
        lastname = None
    if not lastname or len(lastname) < 2:
        return True

    directory_results = selenium_driver.lookup_directory(
        firstname=firstname, lastname=lastname
    )
    if not directory_results:
        return False

    return True
