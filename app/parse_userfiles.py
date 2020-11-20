# parse_userfiles.py


from lxml import etree as ET

from globals import NSMAP

## Helpers


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
        "current_colls": get_current_colls(record_elem),
        "current_depts": get_current_depts(record_elem),
        "person": get_person(record_elem),
        "presentations": get_presentations(record_elem),
        "intellconts": get_intellconts(record_elem),
    }
    return parsed_userfile


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


def get_person(record_elem):
    try:
        PCI_elem = record_elem.xpath("a:PCI", namespaces=NSMAP)[0]
    except IndexError:
        return None

    person = {
        "id": PCI_elem.attrib.get("id"),
        "prefix": get_child_text(PCI_elem, "PREFIX"),
        "firstname": get_child_text(PCI_elem, "FNAME"),
        "middlename": get_child_text(PCI_elem, "MNAME"),
        "lastname": get_child_text(PCI_elem, "LNAME"),
        "suffix": get_child_text(PCI_elem, "SUFFIX"),
        "photo": get_child_text(PCI_elem, "UPLOAD_PHOTO"),
        "endpos": get_child_text(PCI_elem, "ENDPOS"),
    }
    return person


def get_adminperm(record_elem):
    try:
        adminperm_elem = record_elem.xpath("a:ADMIN_PERM", namespaces=NSMAP)[0]
    except IndexError:
        return None

    adminperm = {
        "id": adminperm_elem.attrib.get("id"),
        "srank": get_child_text(adminperm_elem, "SRANK"),
    }
    return adminperm


def get_presentations(record_elem):
    presentation_elems = record_elem.xpath("a:PRESENT", namespaces=NSMAP)
    presentations = [parse_presentation(i) for i in presentation_elems]
    return presentations


def parse_presentation(present_elem):
    presentation = {
        "id": present_elem.attrib.get("id"),
        "present_type": get_child_text(present_elem, "PRESENTATION_TYPE"),
        "name": get_child_text(present_elem, "NAME"),
        "org": get_child_text(present_elem, "ORG"),
        "location": get_child_text(present_elem, "LOCATION"),
        "title": get_child_text(present_elem, "TITLE"),
        "persons_involved": get_persons_involved(present_elem, "PRESENT_AUTH"),
        "collab": get_child_text(present_elem, "COLLAB"),
        "meettype": get_child_text(present_elem, "MEETTYPE"),
        "scope": get_child_text(present_elem, "SCOPE"),
        "refereed": get_child_text(present_elem, "REFEREED"),
        "pubproceed": get_child_text(present_elem, "PUBPROCEED"),
        "pubelse": get_child_text(present_elem, "PUBELSE"),
        "invacc": get_child_text(present_elem, "INVACC"),
        "ceu_credit": get_child_text(present_elem, "CEU_CREDIT"),
        "abstract": get_child_text(present_elem, "ABSTRACT"),
        "date_start": get_child_text(present_elem, "DATE_START"),
        "date_end": get_child_text(present_elem, "DATE_END"),
        "user_reference_creator": get_child_text(
            present_elem, "USER_REFERENCE_CREATOR"
        ),
    }
    return presentation


def get_persons_involved(elem, subelem_name):
    person_elems = elem.xpath(f"a:{subelem_name}", namespaces=NSMAP)
    persons_involved = [parse_person(i) for i in person_elems]
    return persons_involved


def parse_person(person_elem):
    person = {
        "id": get_child_text(person_elem, "FACULTY_NAME"),
        "firstname": get_child_text(person_elem, "FNAME"),
        "middlename": get_child_text(person_elem, "MNAME"),
        "lastname": get_child_text(person_elem, "LNAME"),
        "role": get_child_text(person_elem, "ROLE"),
        "student_level": get_child_text(person_elem, "STUDENT_LEVEL"),
        "institution": get_child_text(person_elem, "INSTITUTION"),
    }
    return person


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
        if i.get("date_end") == "" and i.get("role")
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
        "id": assignment_elem.attrib.get("id"),
        "role": get_child_text(assignment_elem, "ROLE"),
        "scope": get_child_text(assignment_elem, "SCOPE"),
        "desc": get_child_text(assignment_elem, "DESC"),
        "date_start": date_start,
        "date_end": date_end,
    }
    return assignment


def get_intellconts(record_elem):
    intellcont_elems = record_elem.xpath("a:INTELLCONT", namespaces=NSMAP)
    intellconts = [parse_intellcont(i) for i in intellcont_elems]
    return intellconts


def parse_intellcont(intellcont_elem):
    intellcont = {
        "id": intellcont_elem.attrib.get("id"),
        "contype": get_child_text(intellcont_elem, "CONTYPE"),
        "status": get_child_text(intellcont_elem, "STATUS"),
        "title": get_child_text(intellcont_elem, "TITLE"),
        "publisher": get_child_text(intellcont_elem, "PUBLISHER"),
        "date_published": get_child_text(intellcont_elem, "PUB_START"),
        "doi": get_child_text(intellcont_elem, "DOI"),
        "persons_involved": get_persons_involved(intellcont_elem, "INTELLCONT_AUTH"),
        "abstract": get_child_text(intellcont_elem, "ABSTRACT"),
        "volume": get_child_text(intellcont_elem, "VOLUME"),
        "issue": get_child_text(intellcont_elem, "ISSUE"),
        "page_nums": get_child_text(intellcont_elem, "PAGENUM"),
    }
    return intellcont


def get_admins(record_elem):
    admin_elems = record_elem.xpath("a:ADMIN", namespaces=NSMAP)
    admins = [parse_admin(i) for i in admin_elems]
    return admins


def parse_admin(admin_elem):
    admin = {
        "id": admin_elem.attrib.get("id"),
        "ac_year": get_child_text(admin_elem, "AC_YEAR"),
        "date_start": get_child_text(admin_elem, "YEAR_START"),
        "date_end": get_child_text(admin_elem, "YEAR_END"),
        "depts": parse_depts(admin_elem),
        "rank": get_child_text(admin_elem, "RANK"),
        "tenure": get_child_text(admin_elem, "TENURE"),
    }
    return admin


def parse_depts(admin_elem):
    admin_dep_elems = admin_elem.xpath("a:ADMIN_DEP", namespaces=NSMAP)
    depts = [get_child_text(i, "DEP") for i in admin_dep_elems]
    return depts
