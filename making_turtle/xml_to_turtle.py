#!/usr/bin/env python

import os

from lxml import etree as ET
import rdflib
from rdflib import Namespace, URIRef, BNode, Literal
from rdflib.namespace import FOAF, OWL, RDF, RDFS, SKOS, XSD
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

## Globals


NSMAP = {
    "a": "http://www.digitalmeasures.com/schema/data",
    "dmd": "http://www.digitalmeasures.com/schema/data-metadata",
}

NS = Namespace("http://vivo.uncw.edu/individual/")
BIBO = Namespace("http://purl.org/ontology/bibo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

UNIVERSITY = {
    # same logic as EXPECTED_COLL regarding hardcoded uid
    "name": "University of North Carolina - Wilmington",
    "uid": "168540581888",
    "desc": "A description.  Or two, who knows?",
}


COLL_DEPT = {
    # The uids are insignificant, but must not overlap with any uids from the source dataset
    # they also must remain unchanged across different runs of this script
    # since this is a hard problem, I've manually selected some uid's from ADMIN_DEP elems in the source data
    # because ADMIN_DEP uid's are not carried into the vivo import dataset
    # but the ADMIN_DEP uid's are guarenteed to never equal a uid we may carry over.
    # Essentially, trying to hardcode a uid that could never collide with another element's uid.
    # Each org will need to change these uids.  I suggest using id values from the source ADMIN_DEP elements.
    "Academic Affairs": {
        "uid": "168540397570",
        "depts": {
            "Randall Library": "161986105345",
            "Office of the Provost": "161986107393",
            "Office of the Graduate School": "161986109441",
            "Office of Center for Teaching Excellence & Center for Faculty Leadership": "161986111489",
            "Office of Diversity and Inclusion": "161986113537",
            "Office of the Dean, College of Arts and Sciences": "168541734913",
            "Office of International Programs": "161984303106",
            "Office of the Honors College": "14241826817",
            "Womens Resource Center": "161984301058",
            "Office of Undergraduate Studies": "161984296962",
            "Office of Cultural Arts": "161984299010",
        },
    },
    "Cameron School of Business": {
        "uid": "168540397569",
        "depts": {
            "Management": "168541353987",
            "Economics and Finance": "168541353984",
            "Office of the Dean, Cameron School of Business": "168541353986",
            "Business Analytics, Information Systems, and Supply Chain": "195135006723",
            "Accountancy and Business Law": "195135006722",
            "Marketing": "195135006721",
            "Office of the Dean, Cameron School of Business": "168540397570",
        },
    },
    "Chancellor's Office": {
        "uid": "195210027010",
        "depts": {
            "Office of the Chancellor": "195210027009",
            "Office of Diversity and Inclusion": "187931844609",
            "Office of Athletics": "195128840193",
        },
    },
    "College of Arts and Sciences": {
        "uid": "195126493185",
        "depts": {
            "Anthropology": "161981390849",
            "Public and International Affairs": "161981392897",
            "Psychology": "161981394945",
            "Creative Writing": "161981396993",
            "Sociology and Criminology": "161981399041",
            "Environmental Sciences": "161981401089",
            "International Studies": "161981403137",
            "Film Studies": "161981405185",
            "Philosophy and Religion": "161981407233",
            "Communication Studies": "168540702721",
            "Art and Art History": "161979498497",
            "Earth and Ocean Sciences": "161979500545",
            "Music": "167971166209",
            "History": "168541237249",
            "Physics and Physical Oceanography": "161984610306",
            "Mathematics and Statistics": "161984612354",
            "Computer Science": "161984614402",
            "World Languages and Cultures": "161984616450",
            "English": "161984618498",
            "Biology and Marine Biology": "161984620546",
            "Theatre": "161984622594",
            "Chemistry and Biochemistry": "168541431810",
            "Office of the Dean, College of Arts and Sciences": "161979746305",
            "Interdisciplinary": "161979748353",
        },
    },
    "College of Health and Human Services": {
        "uid": "168540348417",
        "depts": {
            "School of Nursing": "161982855170",
            "School of Health and Applied Human Sciences": "161982857218",
            "School of Social Work": "161982859266",
            "Office of the Dean, College of Health and Human Services": "161982859266",
        },
    },
    "Watson College of Education": {
        "uid": "161982863362",
        "depts": {
            "Instructional Technology, Foundations, and Secondary Education": "161982865410",
            "Educational Leadership": "168541026306",
            "Early Childhood, Elementary, Middle, Literacy and Special Education": "161983545345",
            "Office of the Dean, Watson College of Education": "161983547393",
        },
    },
}


## Helpers


def get_child_text(elem, child, ns="a"):
    try:
        text = elem.xpath(f"{ns}:{child}", namespaces=NSMAP)[0].text
    except IndexError:
        text = ""
    if not text:
        text = ""
    return text


## Parsing user files


def parse_userfile(file):
    etree = ET.parse(file)
    data_elem = etree.xpath("/a:Data", namespaces=NSMAP)[0]
    record_elem = data_elem.xpath("a:Record", namespaces=NSMAP)[0]
    # userID is what links an individual across the digitalmeasures dataset
    userId = record_elem.attrib.get("userId")
    username = record_elem.attrib.get("username")
    # users can have more than one college & more than one dept
    # a user without a dept get tagged with their college only
    # a user without a dept or college are mainly only have schoolteach records
    current_colls_elems = record_elem.xpath(
        "dmd:IndexEntry[@indexKey='COLLEGE']", namespaces=NSMAP
    )
    current_colls = parse_dmd_elems(current_colls_elems)
    current_depts_elems = record_elem.xpath(
        "dmd:IndexEntry[@indexKey='DEPARTMENT']", namespaces=NSMAP
    )
    current_depts = parse_dmd_elems(current_depts_elems)
    try:
        PCI_elem = record_elem.xpath("a:PCI", namespaces=NSMAP)[0]
        person = get_PCI_info(PCI_elem)
    except IndexError:
        person = None
    try:
        adminperm_elem = record_elem.xpath("a:ADMIN_PERM", namespaces=NSMAP)[0]
        adminperm = parse_adminperm(adminperm_elem)
    except IndexError:
        adminperm = None
    presentations = get_presentations(record_elem)
    admin_assignments = get_admin_assignments(record_elem)
    if admin_assignments:
        pass
    admins = get_admins(record_elem)
    return {
        "userId": userId,
        "username": username,
        "admins": admins,
        "admin_assignments": admin_assignments,
        "adminperm": adminperm,
        "current_colls": current_colls,
        "current_depts": current_depts,
        "person": person,
        "presentations": presentations,
    }


def parse_dmd_elems(elems):
    if not elems:
        return []
    for elem in elems:
        return [i.attrib.get("text") for i in elems]


def get_PCI_info(PCI_elem):
    uid = PCI_elem.attrib.get("id")
    prefix = get_child_text(PCI_elem, "PREFIX")
    firstname = get_child_text(PCI_elem, "FNAME")
    middlename = get_child_text(PCI_elem, "MNAME")
    lastname = get_child_text(PCI_elem, "LNAME")
    suffix = get_child_text(PCI_elem, "SUFFIX")
    photo = get_child_text(PCI_elem, "UPLOAD_PHOTO")
    endpos = get_child_text(PCI_elem, "ENDPOS")
    return {
        "id": uid,
        "firstname": firstname,
        "middlename": middlename,
        "lastname": lastname,
        "prefix": prefix,
        "suffix": suffix,
        "photo": photo,
        "endpos": endpos,
    }


def parse_adminperm(adminperm_elem):
    uid = adminperm_elem.attrib.get("id")
    srank = get_child_text(adminperm_elem, "SRANK")
    return {"id": uid, "srank": srank}


def get_presentations(record_elem):
    presentation_elems = record_elem.xpath("a:PRESENT", namespaces=NSMAP)
    all_presentations = []
    for i in presentation_elems:
        presentation = parse_presentation(i)
        all_presentations.append(presentation)
    return all_presentations


def parse_presentation(present_elem):
    uid = present_elem.attrib.get("id")
    present_type = get_child_text(present_elem, "PRESENTATION_TYPE")
    name = get_child_text(present_elem, "NAME")
    org = get_child_text(present_elem, "ORG")
    location = get_child_text(present_elem, "LOCATION")
    title = get_child_text(present_elem, "TITLE")
    persons_involved = parse_persons_involved(present_elem)
    collab = get_child_text(present_elem, "COLLAB")
    meettype = get_child_text(present_elem, "MEETTYPE")
    scope = get_child_text(present_elem, "SCOPE")
    refereed = get_child_text(present_elem, "REFEREED")
    pubproceed = get_child_text(present_elem, "PUBPROCEED")
    pubelse = get_child_text(present_elem, "PUBELSE")
    invacc = get_child_text(present_elem, "INVACC")
    ceu_credit = get_child_text(present_elem, "CEU_CREDIT")
    abstract = get_child_text(present_elem, "ABSTRACT")
    date_start = get_child_text(present_elem, "DATE_START")
    date_end = get_child_text(present_elem, "DATE_END")
    user_reference_creator = get_child_text(present_elem, "USER_REFERENCE_CREATOR")
    return {
        "id": uid,
        "present_type": present_type,
        "name": name,
        "org": org,
        "location": location,
        "title": title,
        "persons_involved": persons_involved,
        "collab": collab,
        "meettype": meettype,
        "scope": scope,
        "refereed": refereed,
        "pubproceed": pubproceed,
        "pubelse": pubelse,
        "invacc": invacc,
        "ceu_credit": ceu_credit,
        "abstract": abstract,
        "date_start": date_start,
        "date_end": date_end,
        "user_reference_creator": user_reference_creator,
    }


def parse_persons_involved(elem):
    persons_involved = elem.xpath("a:PRESENT_AUTH", namespaces=NSMAP)
    all_persons = []
    for i in persons_involved:
        uid = get_child_text(i, "FACULTY_NAME")
        firstname = get_child_text(i, "FNAME")
        middlename = get_child_text(i, "MNAME")
        lastname = get_child_text(i, "LNAME")
        role = get_child_text(i, "ROLE")
        student_level = get_child_text(i, "STUDENT_LEVEL")
        all_persons.append(
            {
                "id": uid,
                "firstname": firstname,
                "middlename": middlename,
                "lastname": lastname,
                "role": role,
                "student_level": student_level,
            }
        )
    return all_persons


def get_admin_assignments(record_elem):
    assignment_elems = record_elem.xpath("a:ADMIN_ASSIGNMENTS", namespaces=NSMAP)
    all_assignments = []
    for i in assignment_elems:
        assignment = parse_assignment(i)
        all_assignments.append(assignment)
    return all_assignments


def parse_assignment(assignment_elem):
    uid = assignment_elem.attrib.get("id")
    role = get_child_text(assignment_elem, "ROLE")
    desc = get_child_text(assignment_elem, "DESC")
    date_start = get_child_text(assignment_elem, "START_START") or get_child_text(
        assignment_elem, "START_END"
    )
    date_end = get_child_text(assignment_elem, "END_START") or get_child_text(
        assignment_elem, "END_END"
    )
    return {
        "id": uid,
        "role": role,
        "desc": desc,
        "date_start": date_start,
        "date_end": date_end,
    }


def get_admins(record_elem):
    admin_elems = record_elem.xpath("a:ADMIN", namespaces=NSMAP)
    all_admins = [parse_admin(i) for i in admin_elems]
    return all_admins


def parse_admin(admin_elem):
    uid = admin_elem.attrib.get("id")
    ac_year = get_child_text(admin_elem, "AC_YEAR")
    year_start = get_child_text(admin_elem, "YEAR_START")
    year_end = get_child_text(admin_elem, "YEAR_END")
    college, dept = None, None
    admin_dep_elems = admin_elem.xpath("a:ADMIN_DEP", namespaces=NSMAP)
    depts = [get_child_text(i, "DEP") for i in admin_dep_elems]
    rank = get_child_text(admin_elem, "RANK")
    tenure = get_child_text(admin_elem, "TENURE")
    admin = {
        "id": uid,
        "ac_year": ac_year,
        "date_start": year_start,
        "date_end": year_end,
        "depts": depts,
        "rank": rank,
        "tenure": tenure,
    }
    return admin


## Creating a turtle file


def init_graph():
    graph = rdflib.Graph()
    graph.namespace_manager.bind("vivo", VIVO, override=False)
    graph.namespace_manager.bind("vcard", VCARD, override=False)
    graph.namespace_manager.bind("obo", OBO, override=False)
    return graph


def add_orgs_to_graph(graph):
    univ_elem = NS[UNIVERSITY["uid"]]
    graph.add((univ_elem, RDF.type, VIVO.University))
    graph.add((univ_elem, RDFS.label, Literal(UNIVERSITY["name"])))
    graph.add((univ_elem, VIVO.overview, Literal(UNIVERSITY["desc"])))

    for coll, coll_details in COLL_DEPT.items():
        coll_elem = NS[coll_details["uid"]]
        graph.add((coll_elem, RDF.type, VIVO.College))
        graph.add((univ_elem, OBO.BFO_0000051, coll_elem))
        graph.add((coll_elem, OBO.BFO_0000050, univ_elem))
        graph.add((coll_elem, RDFS.label, Literal(coll)))

        for dept_name, dept_uid in coll_details["depts"].items():
            dept_elem = NS[dept_uid]
            graph.add((dept_elem, RDF.type, VIVO.AcademicDepartment))
            graph.add((coll_elem, OBO.BFO_0000051, dept_elem))
            graph.add((dept_elem, OBO.BFO_0000050, coll_elem))
            graph.add((dept_elem, RDFS.label, Literal(dept_name)))


def add_user_to_graph(parsed_user, graph):
    fac, name, individual, title, admin, latest_colls, latest_depts = (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )

    if parsed_user["userId"]:
        fac = NS[parsed_user["userId"]]
    if parsed_user["person"] and parsed_user["person"]["id"]:
        name = NS[parsed_user["person"]["id"]]
        individual = NS[f"{parsed_user['userId']}a"]
    if parsed_user["adminperm"] and parsed_user["adminperm"]["id"]:
        title = NS[parsed_user["adminperm"]["id"]]

    if fac:
        graph.add((fac, RDF.type, VIVO.FacultyMember))
        if parsed_user["person"]:
            lastname = parsed_user["person"]["lastname"]
            firstname = parsed_user["person"]["firstname"]
            if parsed_user["person"]["middlename"]:
                middlename = parsed_user["person"]["middlename"]
                display_name = f"{lastname}, {firstname} {middlename}"
            else:
                display_name = f"{lastname}, {firstname}"
            graph.add((fac, RDFS.label, Literal(display_name)))
        if individual:
            graph.add((fac, OBO.ARG_2000028, individual))

    use_individual = bool(fac and individual)
    if use_individual:
        graph.add((individual, RDF.type, VCARD.Individual))
        graph.add((individual, OBO.ARG_2000029, fac))
        graph.add((fac, OBO.ARG_2000028, individual))
        use_name = bool(name)
        if use_name:
            graph.add((individual, VCARD.hasName, name))
            graph.add((name, RDF.type, VCARD.Name))
            graph.add(
                (name, VCARD.givenName, Literal(parsed_user["person"]["firstname"]))
            )
            if not parsed_user["person"]["middlename"]:
                middlename_text = ""
            else:
                middlename_text = parsed_user["person"]["middlename"]
            graph.add((name, VIVO.middleName, Literal(middlename_text)))
            graph.add(
                (name, VCARD.familyName, Literal(parsed_user["person"]["lastname"]))
            )
        use_title = bool(title and parsed_user["adminperm"]["srank"])
        if use_title:
            graph.add((individual, VCARD.hasTitle, title))
            graph.add((title, RDF.type, VCARD.Title))
            graph.add((title, VCARD.title, Literal(parsed_user["adminperm"]["srank"])))

    for presentation in parsed_user["presentations"]:
        add_presentations_to_graph(presentation, graph, fac)

    for admin_assignment in parsed_user["admin_assignments"]:
        add_admin_assignment_to_graph(admin_assignment, graph, fac)

    best_coll_depts = find_best_coll_depts(parsed_user)
    if best_coll_depts:
        for num, best_coll_dept in enumerate(best_coll_depts):
            rank = find_rank_in_dept(parsed_user, best_coll_dept["dept_name"])
            pos = NS[f"{parsed_user['userId']}p{num}"]
            coll_uid = NS[best_coll_dept["coll_uid"]]
            dept = NS[best_coll_dept["dept_uid"]]
            graph.add((pos, RDF.type, VIVO.Position))
            graph.add((pos, RDFS.label, Literal(rank)))
            graph.add((pos, VIVO.relates, dept))
            graph.add((dept, VIVO.relatedBy, pos))
            graph.add((pos, VIVO.relates, fac))
            graph.add((fac, VIVO.relatedBy, pos))


def find_best_coll_depts(parsed_user):
    dmd_depts = parsed_user.get("current_depts")
    college_depts_info = [
        match_college(dept) for dept in dmd_depts if (dept and match_college(dept))
    ]

    if college_depts_info:
        return college_depts_info
    return None


def find_rank_in_dept(parsed_user, dept):
    # in the source data, each user has a dozen or so 'admin' elems,
    # each admin elem has data on a year's work at one department
    # We need to find the most recent 'admin' elem with 'rank' data for a given dept.
    # So, First select only the admin elems matching the dept
    # Then order the dept elems by most recent academic year, 'ac_year'
    # Finally spit out the first elem with any 'rank' data
    dept_matches = [
        admin for admin in parsed_user.get("admins") if dept in admin.get("depts")
    ]
    latest_dept_rank = sorted(
        dept_matches, key=lambda x: x.get("ac_year"), reverse=True
    )
    for i in latest_dept_rank:
        rank = i.get("rank")
        if rank:
            return i.get("rank").strip()

    # But some users leave their rank empty in the 'admin' elements
    # So we next try to get it from their 'admin_perm' element.
    # the source data is less accurate for adminperm/srank than for admin/rank.
    try:
        rank = parsed_user["adminperm"]["srank"]
    except TypeError:
        rank = None
    if rank:
        return rank

    # We could look through their 'past_hist' elems for a clue, but signal/noise is low
    # So we just default to no 'rank'
    return ""


def match_college(dept):
    # because users entered the wrong college for their dept in 1/10 files
    # we have to assume they got the dept correct, and manually lookup the coll.
    # we also hardcoded the uid for college & for dept, for consistency
    for coll, bundle in COLL_DEPT.items():
        if dept in bundle.get("depts"):
            return {
                "coll_name": coll,
                "coll_uid": bundle.get("uid"),
                "dept_name": dept,
                "dept_uid": bundle["depts"][dept],
            }
    return None


def add_presentations_to_graph(presentation, graph, fac):
    invited_talk = NS[presentation["id"]]
    conference = NS[f"{presentation['id']}a"]
    attendee_role = NS[f"{presentation['id']}b"]

    datetime_interval = NS[f"{presentation['id']}c"]
    datetime_start = NS[f"{presentation['id']}d"]
    datetime_end = NS[f"{presentation['id']}e"]

    graph.add((fac, OBO.RO_0000053, attendee_role))

    graph.add((conference, RDF.type, BIBO.Conference))
    graph.add((conference, RDFS.label, Literal(presentation["name"])))
    graph.add((conference, OBO.BFO_0000051, invited_talk))
    graph.add((conference, BIBO.organizer, Literal(presentation["org"])))

    graph.add((invited_talk, RDF.type, VIVO.InvitedTalk))
    graph.add((invited_talk, RDFS.label, Literal(presentation["title"])))
    graph.add((invited_talk, OBO.BFO_0000055, attendee_role))
    graph.add((invited_talk, VIVO.description, Literal(presentation["abstract"])))
    graph.add((invited_talk, VIVO.dateTimeInterval, datetime_interval))
    graph.add((invited_talk, OBO.BFO_0000050, conference))

    graph.add((attendee_role, RDF.type, VIVO.AttendeeRole))
    graph.add((attendee_role, OBO.BFO_0000054, invited_talk))
    graph.add((attendee_role, OBO.RO_0000052, fac))
    graph.add((attendee_role, VIVO.dateTimeInterval, datetime_interval))

    graph.add((datetime_interval, RDF.type, VIVO.DateTimeInterval))
    graph.add((datetime_interval, VIVO.start, datetime_start))
    graph.add((datetime_interval, VIVO.end, datetime_end))

    graph.add((datetime_start, RDF.type, VIVO.DateTimeValue))
    graph.add(
        (
            datetime_start,
            VIVO.dateTime,
            Literal(presentation["date_start"], datatype=XSD.date),
        )
    )
    graph.add((datetime_start, VIVO.dateTimePrecision, VIVO.yearPrecision))

    graph.add((datetime_end, RDF.type, VIVO.DateTimeValue))
    graph.add(
        (
            datetime_end,
            VIVO.dateTime,
            Literal(presentation["date_end"], datatype=XSD.date),
        )
    )
    graph.add((datetime_end, VIVO.dateTimePrecision, VIVO.yearPrecision))


def add_admin_assignment_to_graph(admin_assignment, graph, fac):
    position = NS[admin_assignment["id"]]

    datetime_interval = NS[f"{admin_assignment['id']}a"]
    datetime_start = NS[f"{admin_assignment['id']}b"]
    datetime_end = NS[f"{admin_assignment['id']}c"]

    graph.add((position, RDF.type, VIVO.FacultyAdministrativePosition))
    graph.add((position, RDFS.label, Literal(admin_assignment["role"])))
    graph.add((position, VIVO.description, Literal(admin_assignment["desc"])))
    graph.add((position, VIVO.dateTimeInterval, datetime_interval))
    #     graph.add((position, VIVO.relates, #college_elem))
    graph.add((position, VIVO.relates, fac))

    graph.add((datetime_interval, RDF.type, VIVO.DateTimeInterval))
    graph.add((datetime_interval, VIVO.start, datetime_start))
    graph.add((datetime_interval, VIVO.end, datetime_end))

    graph.add((datetime_start, RDF.type, VIVO.DateTimeValue))
    graph.add(
        (
            datetime_start,
            VIVO.dateTime,
            Literal(admin_assignment["date_start"], datatype=XSD.date),
        )
    )
    graph.add((datetime_start, VIVO.dateTimePrecision, VIVO.yearPrecision))

    graph.add((datetime_end, RDF.type, VIVO.DateTimeValue))
    graph.add(
        (
            datetime_end,
            VIVO.dateTime,
            Literal(admin_assignment["date_end"], datatype=XSD.date),
        )
    )
    graph.add((datetime_end, VIVO.dateTimePrecision, VIVO.yearPrecision))


def gather_ignored_users():
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
    return generic_users.union(
        office_staff, IT, IRP, deans_office, name_changed, unknown_404_response
    )


def is_excluded_user(parsed_user, driver):
    if not parsed_user:
        print(f"")
    if is_only_do_not_use(parsed_user):
        print(f"{parsed_user.get('username')} is only do not use")
        return True
    if is_student(parsed_user):
        print(f"{parsed_user.get('username')} is student")
        return True
    if not is_in_directory(parsed_user, driver):
        print(f"{parsed_user.get('username')} is not in directory")
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

    directory_results = search_directory(
        firstname=firstname, lastname=lastname, driver=driver
    )
    if not directory_results:
        return False
    return True


def search_directory(firstname="", lastname="", driver=None):
    if not driver:
        options = Options()
        options.add_argument("-headless")
        driver = webdriver.Firefox(executable_path="geckodriver", options=options)
    driver.get("https://itsappserv01.uncw.edu/directory/")

    radio_elem = driver.find_element_by_id("rdoSearchTable_0")
    firstname_elem = driver.find_element_by_name("txtFirstName")
    lastname_elem = driver.find_element_by_name("txtLastName")
    submit_elem = driver.find_element_by_name("btnSearch")
    radio_elem.send_keys(Keys.ARROW_RIGHT)
    firstname_elem.clear()
    firstname_elem.send_keys(firstname)
    lastname_elem.clear()
    lastname_elem.send_keys(lastname)
    submit_elem.send_keys(Keys.RETURN)

    try:
        response_table = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "gvDirectory"))
        )
    except TimeoutException:
        return []
    response_rows = response_table.find_elements_by_xpath("tbody/tr")

    row_dicts = []
    for num, row in enumerate(response_rows):
        if num == 0:
            continue
        (name, pos, dept, _, email, _) = [
            i.text for i in row.find_elements_by_xpath("td")
        ]
        row_dict = {
            "table_row": num,
            "name": name,
            "pos": pos,
            "dept": dept,
            "email": email,
        }
        row_dicts.append(row_dict)

    return row_dicts


if __name__ == "__main__":
    graph = init_graph()
    ignored_users = gather_ignored_users()
    add_orgs_to_graph(graph)

    options = Options()
    options.add_argument("-headless")
    driver = webdriver.Firefox(executable_path="geckodriver", options=options)

    for filename in sorted(os.listdir("../extracting/output/users/")):
        if filename < "siegelr.xml":
            continue
        if filename.split(".")[0] in ignored_users:
            continue
        parsed_user = parse_userfile(f"../extracting/output/users/{filename}")
        if is_excluded_user(parsed_user, driver):
            continue
        add_user_to_graph(parsed_user, graph)
    driver.close()

    filetext = graph.serialize(format="turtle").decode("utf-8")
    with open("all.ttl", "w") as f:
        f.write(filetext)
