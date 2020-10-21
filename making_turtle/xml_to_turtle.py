#!/usr/bin/env python

import os
from lxml import etree as ET
import rdflib
from rdflib import Namespace, URIRef, BNode, Literal
from rdflib.namespace import FOAF, OWL, RDF, RDFS, SKOS, XSD


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


def gather_ignored_users():
    generic_users = {
        "databackup_service",
        "fac_reports",
        "web_services_vivo",
        "facultytest",
    }
    admin_assistants = {"DIEPPAS", "carabellin", "culpa", "sahljs"}
    IT = {"chapmanc", "luopaj", "powella"}
    IRP = {"cohens", "lawsonw"}
    deans_office = {"wilsonca"}
    name_changed = {"gorea"}
    unknown_reason = {
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
        admin_assistants, IT, IRP, deans_office, name_changed, unknown_reason
    )


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
    current_colls = record_elem.xpath(
        "dmd:IndexEntry[@indexKey='COLLEGE']", namespaces=NSMAP
    )
    current_depts = record_elem.xpath(
        "dmd:IndexEntry[@indexKey='DEPARTMENT']", namespaces=NSMAP
    )
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
    jobs = get_admins(record_elem)
    past_history = get_past_history(record_elem)
    return {
        "userId": userId,
        "username": username,
        "person": person,
        "adminperm": adminperm,
        "presentations": presentations,
        "admin_assignments": admin_assignments,
        "jobs": jobs,
        "current_colls": current_colls,
        "current_depts": current_depts,
        "past_history": past_history,
    }


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
    all_admins = []
    for i in admin_elems:
        admin = parse_admin(i)
        all_admins.append(admin)
    return all_admins


def parse_admin(admin_elem):
    uid = admin_elem.attrib.get("id")
    ac_year = get_child_text(admin_elem, "AC_YEAR")
    year_start = get_child_text(admin_elem, "YEAR_START")
    year_end = get_child_text(admin_elem, "YEAR_END")
    college, dept = None, None
    admin_dep_elems = admin_elem.xpath("a:ADMIN_DEP", namespaces=NSMAP)
    admin_dep = []
    for i in admin_dep_elems:
        college = get_child_text(i, "COLLEGE")
        dept = get_child_text(i, "DEP")
        admin_dep.append({"college": college, "dept": dept})
    rank = get_child_text(admin_elem, "RANK")
    tenure = get_child_text(admin_elem, "TENURE")
    return {
        "id": uid,
        "ac_year": ac_year,
        "date_start": year_start,
        "date_end": year_end,
        "admin_dep": admin_dep,
        "rank": rank,
        "tenure": tenure,
    }


def get_past_history(record_elem):
    past_history_elems = record_elem.xpath("a:PASTHIST", namespaces=NSMAP)
    all_past_history = []
    for elem in past_history_elems:
        past_history = parse_past_history(elem)
        if past_history:
            all_past_history.append(past_history)
    return all_past_history


def parse_past_history(elem):
    org = get_child_text(elem, "ORG")
    title = get_child_text(elem, "TITLE")
    start_date = elem.attrib.get("startDate") or get_child_text(elem, "START_START")
    if not is_uncw_org(org):
        return None
    if not (title and start_date):
        return None
    return {"title": title, "start_date": start_date}


def is_uncw_org(org):
    for i in {
        "uncw",
        "university of north carolina wilmington",
        "unc - wilmington",
        "unc wilmington",
        "univ of north carolina - wilmington",
        "univeristy of north carolina wilmington",
        "unc-wilmington",
        "unversity of north carolina wilmington",
        "university of north carolina wilmingon",
        "university of north carolina wilmingtn",
        "university of north carolina at wilmington",
        "university of north carolina, wilmington",
        "univerity of north carolina wilmington",
        "university north carolina wilmington",
        "university of north carolina  wilmington",
        "university of north carolina-wilmington",
        "university if north carolina wilmington",
    }:
        if i in org.lower():
            return True
    return False


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
        graph.add((univ_elem, OBO.BFO_0000051, coll_elem))
        graph.add((coll_elem, OBO.BFO_0000050, univ_elem))
        graph.add((coll_elem, RDF.type, VIVO.College))
        graph.add((coll_elem, RDFS.label, Literal(coll)))

        for dept_name, dept_uid in coll_details["depts"].items():
            dept_elem = NS[dept_uid]
            graph.add((coll_elem, OBO.BFO_0000051, dept_elem))
            graph.add((dept_elem, OBO.BFO_0000050, coll_elem))
            graph.add((dept_elem, RDF.type, FOAF.Organization))
            graph.add((dept_elem, RDF.type, VIVO.AcademicDepartment))
            graph.add((dept_elem, RDFS.label, Literal(dept_name)))


def add_user_to_graph(parsed_user, graph):
    fac, name, individual, title, jobs, latest_colls, latest_depts = (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    current_position = find_latest_position(parsed_user)

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

    if name:
        graph.add((name, RDF.type, VIVO.Individual))
        graph.add((name, VCARD.givenName, Literal(parsed_user["person"]["firstname"])))
        if not parsed_user["person"]["middlename"]:
            graph.add((name, VIVO.middleName, Literal("")))
        else:
            graph.add(
                (name, VIVO.middleName, Literal(parsed_user["person"]["middlename"]))
            )
        graph.add((name, VCARD.familyName, Literal(parsed_user["person"]["lastname"])))

    if individual:
        graph.add((individual, RDF.type, VCARD.Individual))
        if name:
            graph.add((individual, VCARD.hasName, name))
        if fac:
            graph.add((individual, OBO.ARG_2000029, fac))
        if title:
            graph.add((individual, VCARD.hasTitle, title))

    if title:
        graph.add((title, RDF.type, VCARD.Title))
        if parsed_user["adminperm"]["srank"]:
            graph.add((title, VCARD.title, Literal(parsed_user["adminperm"]["srank"])))

    for presentation in parsed_user["presentations"]:
        add_presentations_to_graph(presentation, graph, fac)

    for admin_assignment in parsed_user["admin_assignments"]:
        add_admin_assignment_to_graph(admin_assignment, graph, fac)

    for job in parsed_user["jobs"]:
        # jobs are split by year into many entries
        # they should be merged, if the same job.
        # I haven't heard that we want to include job history in our vivo
        # so let's skip this part since it's tough & probably not asked for
        break


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


def find_latest_position(parsed_user):
    if not parsed_user["person"]:
        return None

    # check if the user entered their position in "endpos" first
    # except for bad data entried
    false_entries = (
        "na",
        "n/a",
        "n / a",
        "steve zinder",
        "drew rosen",
        "hua li",
        "alexander mcdaniel",
        "james a. lyon",
    )
    try:
        end_position = parsed_user["person"]["endpos"]
    except KeyError:
        end_position = None
    if end_position and end_position.strip().lower() not in false_entries:
        latest_position = parsed_user["person"]["endpos"]
        return latest_position

    # check if the user entered their position in "srank" next
    try:
        srank = parsed_user["adminperm"]["srank"]
    except (KeyError, TypeError):
        srank = None
    if srank:
        return srank

    try:
        past_history = sorted(
            parsed_user["past_history"], key=lambda x: x["start_date"], reverse=True
        )[0]
        title = past_history["title"]
    except IndexError:
        title = None
    if title:
        return title


if __name__ == "__main__":
    graph = init_graph()
    ignored_users = gather_ignored_users()
    add_orgs_to_graph(graph)
    count = 0
    for i in sorted(os.listdir("../extracting/output/users/")):
        if i.split(".")[0] in ignored_users:
            continue
        parsed_user = parse_userfile(f"../extracting/output/users/{i}")
        add_user_to_graph(parsed_user, graph)
        count += 1
        if count > 20:
            break

    filetext = graph.serialize(format="turtle").decode("utf-8")
    with open("all.ttl", "w") as f:
        f.write(filetext)
