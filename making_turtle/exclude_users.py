# exclude_users.py

from scrape_directory import scrape_directory


generic_users = {
    "databackup_service",
    "fac_reports",
    "web_services_vivo",
    "facultytest",
}
office_staff = {
    "DIEPPAS",
    "carabellin",
    "culpa",
    "sahljs",
    "baileyj",
    "beaudoinh",
    "deltsi",
    "grays",
    "hartmanc",
    "lindgrens",
    "murrayd",
    "ramadanik",
    "grays",
    "mcdanielk",
    "wrightlk",
}
IT = {"chapmanc", "luopaj", "powella"}
IRP = {"cohens", "lawsonw", "morristr"}
deans_office = {"wilsonca"}
name_changed = {"gorea"}
unknown_404_response = {
    "braunr",
    "crs5798",
    "gorae",
    "hoadleyd",
    "jarrellb",
    "jrh4152",
    "keepw",
    "knoxj",
    "lambertonc",
    "learw",
    "macleodw",
    "mcb4548",
    "nelsoncl",
    "richardsa",
    "smm9756",
    "stuartal",
    "weisa",
    "wellswd",
    "westgatea",
}

preignored_users = generic_users.union(
    office_staff, IT, IRP, deans_office, name_changed, unknown_404_response
)


def is_excluded_user(parsed_user, driver):
    if not parsed_user:
        return True
    if is_only_do_not_use(parsed_user):
        return True
    if is_student(parsed_user):
        return True
    if not is_in_directory(parsed_user, driver):
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


def is_in_directory(parsed_user, driver):
    # directory requires each namepart have 2+ characters.
    # someone with no lastname can't be found, reasonable
    # same for some one with no firstname.

    # dev code !!!!!!!!
    with open("exclude_users/not_in_directory.txt", "r") as f:
        directory_results = [i.strip() for i in f.readlines()]
    if parsed_user.get("username") in directory_results:
        return False
    return True

    # production code !!!!!!!!!
    try:
        firstname = parsed_user.get("person").get("firstname")
    except AttributeError:
        firstname = None
    if not firstname or len(firstname) < 2:
        return False

    try:
        lastname = parsed_user.get("person").get("lastname")
    except AttributeError:
        lastname = None
    if not lastname or len(lastname) < 2:
        return False

    directory_results = scrape_directory(
        firstname=firstname, lastname=lastname, driver=driver
    )
    if not directory_results:
        return False
    return True
