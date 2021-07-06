# exclude_users.py

import os
import shutil

from scrape_directory import SeleniumDriver
from parse_userfiles import parse_userfile
from graph_builder.make_graph import conjure_coll_dept_assignment


generic_users = {"facultytest"}
IRP = {"morristr"}
office_staff = {
    "armstrongg",
    "baileyj",
    "beaudoinh",
    "deltsi",
    "grays",
    "hartmanc",
    "lindgrens",
    "mcdanielk",
    "murrayd",
    "ramadanik",
    "wrightlk",
}
preignored_users = set().union(generic_users, office_staff, IRP)


def split_include_exclude(source_dir, include_dir, exclude_dir):
    excluded_files = {i for i in os.listdir(exclude_dir)}
    included_files = {i for i in os.listdir(include_dir)}
    already_processed = excluded_files.union(included_files)

    selenium_driver = SeleniumDriver()

    all_filenames = sorted(os.listdir(source_dir))
    for filename in all_filenames:
        if filename in already_processed:
            continue
        if is_exclude(source_dir, filename, selenium_driver):
            copy(source_dir, exclude_dir, filename)
        else:
            copy(source_dir, include_dir, filename)

    selenium_driver.driver.quit()

    return include_dir, exclude_dir


def is_exclude(source_dir, filename, selenium_driver):
    username = filename.split(".")[0]
    if username in preignored_users:
        return True

    filepath = os.path.join(source_dir, filename)
    parsed_user = parse_userfile(filepath)

    if not parsed_user:
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


def is_only_do_not_use(parsed_user):
    # some users have a department name with the text "DO NOT USE"
    # exclude the user if all their departments names are such
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
    # loop through them all, and unflag if any match.
    exclude = True
    for i in likely_coll_dept:
        if i["coll_name"] == "College of Health and Human Services":
            exclude = False
        if i["dept_name"] == "Randall Library":
            exclude = False
    if exclude:
        return True


def is_in_directory(parsed_user, selenium_driver):
    # directory requires each namepart have 2+ characters.
    # someone with short lastname can't be found.
    # same for some one with short firstname.
    # Erring on the side of including those with short names.

    # DEV CODE !!!!!!!!
    # with open("exclude_users/not_in_directory.txt", "r") as f:
    #     directory_results = [i.strip() for i in f.readlines()]
    # if parsed_user.get("username") in directory_results:
    #     return False
    # return True

    # production code !!!!!!!!!
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
        # print(parsed_user.get("username"))
        return False

    return True


def copy(source_dir, dest_dir, filename):
    source = os.path.join(source_dir, filename)
    dest = os.path.join(dest_dir, filename)
    shutil.copy2(source, dest)
