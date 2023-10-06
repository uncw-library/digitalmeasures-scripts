# parse_userfiles.py

import json
import logging
import os
import pprint

from lxml import etree as ET

from globals import NSMAP


## Helpers

DISPLAYING_INTELLCONTS_BUT_SHOULD_BE_HIDDEN = {'cardenasj', 'chenyj', 'choij', 'eshlemanm', 'framptona', 'freudemana', 'gambled', 'irvinen', 'kamels', 'kerrj', 'kongy', 'mcbrayerl', 'monahand', 'porcoa', 'rigginsa', 'sardinaa', 'sellonm', 'sutterl', 'turrises', 'vetterr', 'yopakk'}

def parse_dmd_elems(elems):
    if not elems:
        return []
    for elem in elems:
        return [i.attrib.get("text") for i in elems]


def get_child_text(elem, child, ns="a"):
    try:
        text = elem.xpath(f"{ns}:{child}", namespaces=NSMAP)[0].text
    except IndexError:
        return ""
    if not text:
        return ""
    return text


def parse_and_pretty_print(source_dir, output_dir):
    all_filenames = sorted(os.listdir(source_dir))
    for filename in all_filenames:
        parsed_user = parse_userfile(os.path.join(source_dir, filename))
        file, ext = os.path.splitext(filename)

        # WFS API is bugged.  Sending us garbled "PUBAVAIL" message.
        # These faculty have NO on some records, so taking a sledgehammer approach by clearing out all their intellconts
        if file in DISPLAYING_INTELLCONTS_BUT_SHOULD_BE_HIDDEN:
            parsed_user["intellconts"] = []


        dest_filepath = os.path.join(output_dir, f"{file}.json")
        json_text = json.dumps(parsed_user, indent=2, sort_keys=True)
        with open(dest_filepath, "w") as f:
            f.write(json_text)
    logging.info("parse and prettyprint complete")


def get_persons_involved(elem, subelem_name):
    person_elems = elem.xpath(f"a:{subelem_name}", namespaces=NSMAP)
    persons_involved = [parse_person(i) for i in person_elems]
    return persons_involved


def parse_person(person_elem):
    person = {
        "id": get_child_text(person_elem, "FACULTY_NAME"),
        "role": get_child_text(person_elem, "ROLE")
        or get_child_text(person_elem, "CONTRIBUTION"),
        # "firstname": get_child_text(person_elem, "FNAME"),
        # "middlename": get_child_text(person_elem, "MNAME"),
        # "lastname": get_child_text(person_elem, "LNAME"),
        # "student_level": get_child_text(person_elem, "STUDENT_LEVEL"),
        # "institution": get_child_text(person_elem, "INSTITUTION"),
    }
    return person


## Actual code


def parse_userfile(file):
    # userID is what links an individual across the digitalmeasures dataset
    etree = ET.parse(file)
    data_elem = etree.xpath("/a:Data", namespaces=NSMAP)[0]
    record_elem = data_elem.xpath("a:Record", namespaces=NSMAP)[0]

    parsed_userfile = {
        "userId": record_elem.attrib.get("userId"),
        "username": record_elem.attrib.get("username"),
        "admins": get_admins(record_elem),
        "admin_assignments": get_admin_assignments(record_elem),
        "adminperm": get_adminperm(record_elem),
        "congrants": get_contgrants(record_elem),
        "current_colls": get_current_colls(record_elem),
        "current_depts": get_current_depts(record_elem),
        "intellprops": get_intellprops(record_elem),
        "perform_exhibits": get_perform_exhibits(record_elem),
        "person": get_person(record_elem),
        "presentations": get_presentations(record_elem),
        "intellconts": get_intellconts(record_elem),
    }
    return parsed_userfile


def get_admins(record_elem):
    admin_elems = record_elem.xpath("a:ADMIN", namespaces=NSMAP)
    admins = [parse_admin(i) for i in admin_elems]
    return admins


def parse_admin(admin_elem):
    admin = {
        "ac_year": get_child_text(admin_elem, "AC_YEAR"),
        "depts": parse_depts(admin_elem),
        "rank": get_child_text(admin_elem, "RANK"),
        # "id": admin_elem.attrib.get("id"),
        # "date_start": get_child_text(admin_elem, "YEAR_START"),
        # "date_end": get_child_text(admin_elem, "YEAR_END"),
        # "tenure": get_child_text(admin_elem, "TENURE"),
    }
    return admin


def parse_depts(admin_elem):
    admin_dep_elems = admin_elem.xpath("a:ADMIN_DEP", namespaces=NSMAP)
    depts = [get_child_text(i, "DEP") for i in admin_dep_elems]
    return depts


def get_admin_assignments(record_elem):
    # Active assignments have "" as date_end.
    # only include active assignment_elems.
    # no assignment_elems have a None date_end (moot).
    # past assignments have "yyyy-mm-dd" date_end, and are excluded.
    #
    # Some elem have an empty 'role' value
    # but we can't make sense of that, so exclude them.
    assignment_elems = record_elem.xpath("a:ADMIN_ASSIGNMENTS", namespaces=NSMAP)
    admin_assignments = [
        parse_assignment(i)
        for i in assignment_elems
        if parse_assignment(i).get("date_end") == "" and parse_assignment(i).get("role")
    ]
    return admin_assignments


def parse_assignment(assignment_elem):
    date_start = get_child_text(assignment_elem, "START_START") or get_child_text(
        assignment_elem, "START_END"
    )
    date_end = get_child_text(assignment_elem, "END_START") or get_child_text(
        assignment_elem, "END_END"
    )
    assignment = {
        "date_start": date_start,
        "date_end": date_end,
        "desc": get_child_text(assignment_elem, "DESC"),
        "id": assignment_elem.attrib.get("id"),
        "role": get_child_text(assignment_elem, "ROLE"),
        "scope": get_child_text(assignment_elem, "SCOPE"),
    }
    return assignment


def get_adminperm(record_elem):
    try:
        adminperm_elem = record_elem.xpath("a:ADMIN_PERM", namespaces=NSMAP)[0]
    except IndexError:
        return None

    adminperm = {
        "id": adminperm_elem.attrib.get("id"),
        "srank": get_child_text(adminperm_elem, "SRANK"),
        # "dty_separation": get_child_text(adminperm_elem, "DTY_SEPARATION"),
    }
    return adminperm


def get_contgrants(record_elem):
    congrant_elems = record_elem.xpath("a:CONGRANT", namespaces=NSMAP)
    congrants = [parse_congrant(i) for i in congrant_elems]
    return congrants


def parse_congrant(congrant_elem):
    date_filed = get_child_text(congrant_elem, "SUB_START") or get_child_text(
        congrant_elem, "SUB_END"
    )
    date_issued_start = get_child_text(congrant_elem, "START_START") or get_child_text(
        congrant_elem, "START_START"
    )
    date_issued_end = get_child_text(congrant_elem, "END_START") or get_child_text(
        congrant_elem, "END_END"
    )

    congrant = {
        "id": congrant_elem.attrib.get("id"),
        "date_filed": date_filed,
        "date_issued_start": date_issued_start,
        "date_issued_end": date_issued_end,
        "abstract": get_child_text(congrant_elem, "ABSTRACT"),
        "amount": get_child_text(congrant_elem, "AMOUNT"),
        "persons_involved": get_persons_involved(congrant_elem, "CONGRANT_INVEST"),
        "status": get_child_text(congrant_elem, "STATUS"),
        "title": get_child_text(congrant_elem, "TITLE"),
        # "awardorg": get_child_text(congrant_elem, "AWARDORG"),
        # "classification": get_child_text(congrant_elem, "CLASSIFICATION"),
        # "dtd_end": get_child_text(congrant_elem, "DTD_END"),
        # "dtd_start": get_child_text(congrant_elem, "DTD_START"),
        # "dtd_sub": get_child_text(congrant_elem, "DTD_SUB"),
        # "dtm_end": get_child_text(congrant_elem, "DTM_END"),
        # "dtm_start": get_child_text(congrant_elem, "DTM_START"),
        # "dtm_sub": get_child_text(congrant_elem, "DTM_SUB"),
        # "dty_end": get_child_text(congrant_elem, "DTY_END"),
        # "dty_start": get_child_text(congrant_elem, "DTY_START"),
        # "dty_sub": get_child_text(congrant_elem, "DTY_SUB"),
        # "partner": get_child_text(congrant_elem, "PARTNER"),
        # "sponorg": get_child_text(congrant_elem, "SPONORG"),
        # "teaching_related": get_child_text(congrant_elem, "TEACHING_RELATED"),
        # "type": get_child_text(congrant_elem, "TYPE"),
        # "user_reference_creator": get_child_text(
        #     congrant_elem, "USER_REFERENCE_CREATOR"
        # ),
    }
    return congrant


def get_current_colls(record_elem):
    current_colls_elems = record_elem.xpath(
        "dmd:IndexEntry[@indexKey='COLLEGE']", namespaces=NSMAP
    )
    current_colls = parse_dmd_elems(current_colls_elems)
    return current_colls


def get_current_depts(record_elem):
    current_depts_elems = record_elem.xpath(
        "dmd:IndexEntry[@indexKey='DEPARTMENT']", namespaces=NSMAP
    )
    current_depts = parse_dmd_elems(current_depts_elems)
    return current_depts


def get_intellprops(record_elem):
    intellprop_elems = record_elem.xpath("a:INTELLPROP", namespaces=NSMAP)
    intellprops = [parse_intellprop(i) for i in intellprop_elems]
    return intellprops


def parse_intellprop(intellprop_elem):
    intellprops = {
        "id": intellprop_elem.attrib.get("id"),
        "application_end": get_child_text(intellprop_elem, "APPLICATION_END"),
        "application_start": get_child_text(intellprop_elem, "APPLICATION_START"),
        "approve_end": get_child_text(intellprop_elem, "APPROVE_END"),
        "approve_start": get_child_text(intellprop_elem, "APPROVE_START"),
        "format": get_child_text(intellprop_elem, "FORMAT"),
        "id_number": get_child_text(intellprop_elem, "ID_NUMBER"),
        "persons_involved": get_persons_involved(intellprop_elem, "INTELLPROP_INVENT"),
        "title": get_child_text(intellprop_elem, "TITLE"),
        # "dtd_application": get_child_text(intellprop_elem, "DTD_APPLICATION"),
        # "dtd_approve": get_child_text(intellprop_elem, "DTD_APPROVE"),
        # "dtd_license": get_child_text(intellprop_elem, "DTD_LICENSE"),
        # "dtd_renewal": get_child_text(intellprop_elem, "DTD_RENEWAL"),
        # "dtd_submit": get_child_text(intellprop_elem, "DTD_SUBMIT"),
        # "dtm_application": get_child_text(intellprop_elem, "DTM_APPLICATION"),
        # "dtm_approve": get_child_text(intellprop_elem, "DTM_APPROVE"),
        # "dtm_license": get_child_text(intellprop_elem, "DTM_LICENSE"),
        # "dtm_renewal": get_child_text(intellprop_elem, "DTM_RENEWAL"),
        # "dtm_submit": get_child_text(intellprop_elem, "DTM_SUBMIT"),
        # "dty_application": get_child_text(intellprop_elem, "DTY_APPLICATION"),
        # "dty_approve": get_child_text(intellprop_elem, "DTY_APPROVE"),
        # "dty_license": get_child_text(intellprop_elem, "DTY_LICENSE"),
        # "dty_renewal": get_child_text(intellprop_elem, "DTY_RENEWAL"),
        # "dty_submit": get_child_text(intellprop_elem, "DTY_SUBMIT"),
        # "license_end": get_child_text(intellprop_elem, "LICENSE_END"),
        # "license_start": get_child_text(intellprop_elem, "LICENSE_START"),
        # "nationality": get_child_text(intellprop_elem, "NATIONALITY"),
        # "nations": get_child_text(intellprop_elem, "NATIONS"),
        # "renewal_end": get_child_text(intellprop_elem, "RENEWAL_END"),
        # "renewal_start": get_child_text(intellprop_elem, "RENEWAL_START"),
        # "submit_end": get_child_text(intellprop_elem, "SUBMIT_END"),
        # "submit_start": get_child_text(intellprop_elem, "SUBMIT_START"),
        # "type": get_child_text(intellprop_elem, "TYPE"),
        # "user_reference_creator": get_child_text(
        #     intellprop_elem, "USER_REFERENCE_CREATOR"
        # ),
        # "whom_assigned": get_child_text(intellprop_elem, "WHOM_ASSIGNED"),
        # "whom_licensed": get_child_text(intellprop_elem, "WHOM_LICENSED"),
    }
    return intellprops


def get_perform_exhibits(record_elem):
    perform_exhibit_elems = record_elem.xpath("a:PERFORM_EXHIBIT", namespaces=NSMAP)
    perform_exhibits = [parse_perform_exhibit(i) for i in perform_exhibit_elems]
    return perform_exhibits


def parse_perform_exhibit(perform_exhibit_elem):
    date_start = get_child_text(perform_exhibit_elem, "START_START") or get_child_text(
        perform_exhibit_elem, "START_END"
    )
    date_end = get_child_text(perform_exhibit_elem, "END_START") or get_child_text(
        perform_exhibit_elem, "END_END"
    )

    perform_exhibit = {
        "id": perform_exhibit_elem.attrib.get("id"),
        "date_start": date_start,
        "date_end": date_end,
        "desc": get_child_text(perform_exhibit_elem, "DESC"),
        "name": get_child_text(perform_exhibit_elem, "NAME"),
        "persons_involved": get_persons_involved(
            perform_exhibit_elem, "PERFORM_EXHIBIT_CONTRIBUTERS"
        ),
        "sponsor": get_child_text(perform_exhibit_elem, "SPONSOR"),
        "title": get_child_text(perform_exhibit_elem, "TITLE"),
        # "academic": get_child_text(perform_exhibit_elem, "ACADEMIC"),
        # "delivery_type": get_child_text(perform_exhibit_elem, "DELIVERY_TYPE"),
        # "dtd_end": get_child_text(perform_exhibit_elem, "DTD_END"),
        # "dtd_start": get_child_text(perform_exhibit_elem, "DTD_START"),
        # "dtm_end": get_child_text(perform_exhibit_elem, "DTM_END"),
        # "dtm_start": get_child_text(perform_exhibit_elem, "DTM_START"),
        # "dty_end": get_child_text(perform_exhibit_elem, "DTY_END"),
        # "dty_start": get_child_text(perform_exhibit_elem, "DTY_START"),
        # "invacc": get_child_text(perform_exhibit_elem, "INVACC"),
        # "location": get_child_text(perform_exhibit_elem, "LOCATION"),
        # "refereed": get_child_text(perform_exhibit_elem, "REFEREED"),
        # "scope": get_child_text(perform_exhibit_elem, "SCOPE"),
        # "type": get_child_text(perform_exhibit_elem, "TYPE"),
        # "type_other": get_child_text(perform_exhibit_elem, "TYPE_OTHER"),
        # "user_reference_creator": get_child_text(
        #     perform_exhibit_elem, "USER_REFERENCE_CREATOR"
        # ),
    }
    return perform_exhibit


def get_person(record_elem):
    try:
        PCI_elem = record_elem.xpath("a:PCI", namespaces=NSMAP)[0]
    except IndexError:
        return None

    person = {
        "id": PCI_elem.attrib.get("id"),
        "firstname": get_child_text(PCI_elem, "FNAME"),
        "middlename": get_child_text(PCI_elem, "MNAME"),
        "lastname": get_child_text(PCI_elem, "LNAME"),
        "bio": get_child_text(PCI_elem, "BIO"),
        "teaching_interests": get_child_text(PCI_elem, "TEACHING_INTERESTS"),
        "research_interests": get_child_text(PCI_elem, "RESEARCH_INTERESTS"),
        "photo_url": get_child_text(PCI_elem, "UPLOAD_PHOTO"),
        "ophone1": get_child_text(PCI_elem, "OPHONE1"),
        "ophone2": get_child_text(PCI_elem, "OPHONE2"),
        "ophone3": get_child_text(PCI_elem, "OPHONE3"),
        "email": get_child_text(PCI_elem, "EMAIL"),
        # "prefix": get_child_text(PCI_elem, "PREFIX"),
        # "suffix": get_child_text(PCI_elem, "SUFFIX"),
        # "endpos": get_child_text(PCI_elem, "ENDPOS"),
    }
    return person


def get_presentations(record_elem):
    presentation_elems = record_elem.xpath("a:PRESENT", namespaces=NSMAP)
    presentations = [parse_presentation(i) for i in presentation_elems]
    return presentations


def parse_presentation(present_elem):
    presentation = {
        "id": present_elem.attrib.get("id"),
        "abstract": get_child_text(present_elem, "ABSTRACT"),
        "date_start": get_child_text(present_elem, "DATE_START"),
        "date_end": get_child_text(present_elem, "DATE_END"),
        "name": get_child_text(present_elem, "NAME"),
        "org": get_child_text(present_elem, "ORG"),
        "persons_involved": get_persons_involved(present_elem, "PRESENT_AUTH"),
        "title": get_child_text(present_elem, "TITLE"),
        # "collab": get_child_text(present_elem, "COLLAB"),
        # "location": get_child_text(present_elem, "LOCATION"),
        # "meettype": get_child_text(present_elem, "MEETTYPE"),
        # "scope": get_child_text(present_elem, "SCOPE"),
        # "refereed": get_child_text(present_elem, "REFEREED"),
        # "present_type": get_child_text(present_elem, "PRESENTATION_TYPE"),
        # "pubproceed": get_child_text(present_elem, "PUBPROCEED"),
        # "pubelse": get_child_text(present_elem, "PUBELSE"),
        # "invacc": get_child_text(present_elem, "INVACC"),
        # "ceu_credit": get_child_text(present_elem, "CEU_CREDIT"),
        # "user_reference_creator": get_child_text(
        #     present_elem, "USER_REFERENCE_CREATOR"
        # ),
    }
    return presentation


def get_intellconts(record_elem):
    intellcont_elems = record_elem.xpath("a:INTELLCONT", namespaces=NSMAP)
    intellconts = [parse_intellcont(i) for i in intellcont_elems]
    return intellconts


def parse_intellcont(intellcont_elem):
    intellcont = {
        "id": intellcont_elem.attrib.get("id"),
        "abstract": get_child_text(intellcont_elem, "ABSTRACT"),
        "contype": get_child_text(intellcont_elem, "CONTYPE"),
        "date_published": get_child_text(intellcont_elem, "PUB_START"),
        "doi": get_child_text(intellcont_elem, "DOI"),
        "issue": get_child_text(intellcont_elem, "ISSUE"),
        "page_nums": get_child_text(intellcont_elem, "PAGENUM"),
        "persons_involved": get_persons_involved(intellcont_elem, "INTELLCONT_AUTH"),
        "public_avail": get_child_text(intellcont_elem, "PUBLICAVAIL"),
        "publisher": get_child_text(intellcont_elem, "PUBLISHER"),
        "status": get_child_text(intellcont_elem, "STATUS"),
        "title": get_child_text(intellcont_elem, "TITLE"),
        "title_secondary": get_child_text(intellcont_elem, "TITLE_SECONDARY"),
        "volume": get_child_text(intellcont_elem, "VOLUME"),
    }
    return intellcont
