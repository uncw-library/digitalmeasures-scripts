# parse_userfiles.py


from lxml import etree as ET

from globals import NSMAP


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
    intellconts = get_intellconts(record_elem)
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
        "intellconts": intellconts,
    }


def get_child_text(elem, child, ns="a"):
    try:
        text = elem.xpath(f"{ns}:{child}", namespaces=NSMAP)[0].text
    except IndexError:
        text = ""
    if not text:
        text = ""
    return text


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
    persons_involved = parse_persons_involved(present_elem, "PRESENT_AUTH")
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


def parse_persons_involved(elem, subelem_name):
    persons_involved = elem.xpath(f"a:{subelem_name}", namespaces=NSMAP)
    all_persons = []
    for i in persons_involved:
        uid = get_child_text(i, "FACULTY_NAME")
        firstname = get_child_text(i, "FNAME")
        middlename = get_child_text(i, "MNAME")
        lastname = get_child_text(i, "LNAME")
        role = get_child_text(i, "ROLE")
        institution = get_child_text(i, "INSTITUTION")
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
        date_end = assignment.get("date_end")
        role = assignment.get("role")
        if date_end != "":
            # active assignments have '' as date_end.
            # only include active assignment_elems.
            # no assignment_elems have a None date_end (moot).
            # past assignments have 'yyyy-mm-dd' date_end, and are excluded.
            continue
        if not role:
            # Some elem have an empty 'role' value
            # but we can't make sense of that, so exclude them.
            continue
        all_assignments.append(assignment)
    return all_assignments


def parse_assignment(assignment_elem):
    uid = assignment_elem.attrib.get("id")
    role = get_child_text(assignment_elem, "ROLE")
    scope = get_child_text(assignment_elem, "SCOPE")
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
        "scope": scope,
        "desc": desc,
        "date_start": date_start,
        "date_end": date_end,
    }


def get_intellconts(record_elem):
    intellcont_elems = record_elem.xpath("a:INTELLCONT", namespaces=NSMAP)
    all_intellconts = []
    for i in intellcont_elems:
        intellcont = parse_intellcont(i)
        all_intellconts.append(intellcont)
    return all_intellconts


def parse_intellcont(intellcont_elem):
    uid = intellcont_elem.attrib.get("id")
    contype = get_child_text(intellcont_elem, "CONTYPE")
    status = get_child_text(intellcont_elem, "STATUS")
    title = get_child_text(intellcont_elem, "TITLE")
    publisher = get_child_text(intellcont_elem, "PUBLISHER")
    date_published = get_child_text(intellcont_elem, "PUB_START")
    doi = get_child_text(intellcont_elem, "DOI")
    abstract = get_child_text(intellcont_elem, "ABSTRACT")
    volume = get_child_text(intellcont_elem, "VOLUME")
    issue = get_child_text(intellcont_elem, "ISSUE")
    page_nums = get_child_text(intellcont_elem, "PAGENUM")

    authors_elems = intellcont_elem.xpath("a:INTELLCONT_AUTH", namespaces=NSMAP)
    persons_involved = parse_persons_involved(intellcont_elem, "INTELLCONT_AUTH")
    intellcont = {
        "id": uid,
        "contype": contype,
        "status": status,
        "title": title,
        "publisher": publisher,
        "date_published": date_published,
        "doi": doi,
        "persons_involved": persons_involved,
        "abstract": abstract,
        "volume": volume,
        "issue": issue,
        "page_nums": page_nums,
    }
    return intellcont


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
