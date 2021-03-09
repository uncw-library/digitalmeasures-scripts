# make_turtle.py

import random

import rdflib
from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO, VCARD
from globals import UNIVERSITY, ACADEMIC_AFFAIRS, COLL_DEPT


def init_graph():
    graph = rdflib.Graph()
    graph.namespace_manager.bind("vivo", VIVO, override=False)
    graph.namespace_manager.bind("vcard", VCARD, override=False)
    graph.namespace_manager.bind("obo", OBO, override=False)
    return graph


def add_orgs_to_graph(graph):
    # Our organization structure is University->Division->College->AcademicDepartment
    univ_elem = NS[UNIVERSITY["uid"]]
    graph.add((univ_elem, RDF.type, VIVO.University))
    graph.add((univ_elem, RDFS.label, Literal(UNIVERSITY["name"])))
    graph.add((univ_elem, VIVO.overview, Literal(UNIVERSITY["desc"])))

    division_elem = NS[ACADEMIC_AFFAIRS["uid"]]
    graph.add((division_elem, RDF.type, VIVO.Division))
    graph.add((division_elem, RDFS.label, Literal(ACADEMIC_AFFAIRS["name"])))
    graph.add((division_elem, VIVO.overview, Literal(ACADEMIC_AFFAIRS["desc"])))
    graph.add((univ_elem, OBO.BFO_0000051, division_elem))
    graph.add((division_elem, OBO.BFO_0000050, univ_elem))

    for dept_name, dept_uid in ACADEMIC_AFFAIRS["depts"].items():
        dept_elem = NS[dept_uid]
        graph.add((dept_elem, RDF.type, VIVO.AcademicDepartment))
        graph.add((dept_elem, RDFS.label, Literal(dept_name)))
        graph.add((dept_elem, OBO.BFO_0000050, division_elem))
        graph.add((division_elem, OBO.BFO_0000051, dept_elem))

    for coll, coll_details in COLL_DEPT.items():
        coll_elem = NS[coll_details["uid"]]
        graph.add((coll_elem, RDF.type, VIVO.College))
        graph.add((division_elem, OBO.BFO_0000051, coll_elem))
        graph.add((coll_elem, OBO.BFO_0000050, division_elem))
        graph.add((coll_elem, RDFS.label, Literal(coll)))

        for dept_name, dept_uid in coll_details["depts"].items():
            dept_elem = NS[dept_uid]
            graph.add((dept_elem, RDF.type, VIVO.AcademicDepartment))
            graph.add((dept_elem, RDFS.label, Literal(dept_name)))
            graph.add((dept_elem, OBO.BFO_0000050, coll_elem))
            graph.add((coll_elem, OBO.BFO_0000051, dept_elem))


def add_user_to_graph(graph, parsed_user):
    """
    fac is the person-as-employed -- Everything about a person that's tied to a job position.
    individual is the person-as-organism
    """
    user_id = parsed_user["userId"]
    fac = NS[user_id]
    individual = NS[f"{user_id}a"]
    coll_dept_guess = conjure_coll_dept_assignment(parsed_user)

    """
    Abort processing any person's record if it lacks a userId + person.id + department assignment
    """
    if not parsed_user["userId"]:
        return
    if not (parsed_user["person"] and parsed_user["person"]["id"]):
        return
    if not coll_dept_guess:
        return

    add_person_info_to_graph(graph, parsed_user, fac, individual)
    add_personal_interests_to_graph(graph, parsed_user, fac)
    add_job_positions_to_graph(graph, parsed_user, fac, individual, coll_dept_guess)

    for admin_assignment in parsed_user["admin_assignments"]:
        add_admin_assignment_to_graph(graph, admin_assignment, fac, coll_dept_guess)
    for presentation in parsed_user["presentations"]:
        add_presentations_to_graph(graph, presentation, fac)
    for intellcont in parsed_user["intellconts"]:
        add_intellcont_to_graph(graph, intellcont, fac)
    for perform_exhibit in parsed_user["perform_exhibits"]:
        add_perform_exhibit_to_graph(graph, perform_exhibit, fac)
    for intellprop in parsed_user["intellprops"]:
        add_intellprop_to_graph(graph, intellprop)
    for congrant in parsed_user["congrants"]:
        add_congrant_to_graph(graph, congrant, user_id)


def add_person_info_to_graph(graph, parsed_user, fac, individual):
    name = NS[parsed_user["person"]["id"]]
    lastname = parsed_user["person"]["lastname"]
    firstname = parsed_user["person"]["firstname"]
    if parsed_user["person"]["middlename"]:
        middlename = parsed_user["person"]["middlename"]
        display_name = f"{lastname}, {firstname} {middlename}"
    else:
        middlename = ""
        display_name = f"{lastname}, {firstname}"

    graph.add((fac, RDF.type, VIVO.FacultyMember))
    graph.add((fac, RDFS.label, Literal(display_name)))

    graph.add((fac, OBO.ARG_2000028, individual))
    graph.add((individual, OBO.ARG_2000029, fac))
    graph.add((individual, RDF.type, VCARD.Individual))

    graph.add((individual, VCARD.hasName, name))
    graph.add((name, RDF.type, VCARD.Name))
    graph.add((name, VCARD.givenName, Literal(firstname)))
    graph.add((name, VIVO.middleName, Literal(middlename)))
    graph.add((name, VCARD.familyName, Literal(lastname)))


def add_personal_interests_to_graph(graph, parsed_user, fac):
    bio = parsed_user["person"]["bio"]
    if bio:
        graph.add((fac, VIVO.overview, Literal(bio)))
    teaching_interests = parsed_user["person"]["teaching_interests"]
    if teaching_interests:
        graph.add((fac, VIVO.teachingOverview, Literal(teaching_interests)))
    research_interests = parsed_user["person"]["research_interests"]
    if research_interests:
        graph.add((fac, VIVO.researchOverview, Literal(research_interests)))


def add_job_positions_to_graph(graph, parsed_user, fac, individual, coll_dept_guess):
    if parsed_user["adminperm"] and parsed_user["adminperm"]["id"]:
        title = NS[parsed_user["adminperm"]["id"]]
    else:
        title = NS[f"{parsed_user['userId']}t"]

    for num, best_coll_dept in enumerate(coll_dept_guess):
        rank = find_rank_in_dept(parsed_user, best_coll_dept["dept_name"])
        pos = NS[f"{parsed_user['userId']}p{num}"]
        dept = NS[best_coll_dept["dept_uid"]]
        graph.add((pos, RDF.type, VIVO.Position))
        graph.add((pos, RDFS.label, Literal(rank)))
        graph.add((pos, VIVO.relates, dept))
        graph.add((dept, VIVO.relatedBy, pos))
        graph.add((pos, VIVO.relates, fac))
        graph.add((fac, VIVO.relatedBy, pos))
        # VCARD.Title maps to 'Preferred Title' Vivo subheader
        graph.add((individual, VCARD.hasTitle, title))
        graph.add((title, RDF.type, VCARD.Title))
        graph.add((title, VCARD.title, Literal(rank)))


def add_admin_assignment_to_graph(graph, admin_assignment, fac, coll_dept_guess):
    position = NS[admin_assignment["id"]]

    scope = admin_assignment.get("scope")
    if scope == "Department":
        org = NS[coll_dept_guess[0]["dept_uid"]]
    elif scope == "College":
        org = NS[coll_dept_guess[0]["coll_uid"]]
    elif scope == "University":
        org = NS[UNIVERSITY["uid"]]
    else:
        org = None

    datetime_interval = NS[f"{admin_assignment['id']}a"]
    datetime_start = NS[f"{admin_assignment['id']}b"]
    datetime_end = NS[f"{admin_assignment['id']}c"]

    graph.add((position, RDF.type, VIVO.FacultyAdministrativePosition))
    graph.add((position, RDFS.label, Literal(admin_assignment["role"])))
    graph.add((position, VIVO.description, Literal(admin_assignment["desc"])))
    graph.add((position, VIVO.dateTimeInterval, datetime_interval))
    if org:
        graph.add((position, VIVO.relates, org))
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


def add_presentations_to_graph(graph, presentation, fac):
    presentation_id = presentation["id"]
    invited_talk = NS[presentation_id]
    conference = NS[f"{presentation_id}a"]
    attendee_role = NS[f"{presentation_id}b"]

    datetime_interval = NS[f"{presentation_id}c"]
    datetime_start = NS[f"{presentation_id}d"]
    datetime_end = NS[f"{presentation_id}e"]

    graph.add((conference, RDF.type, BIBO.Conference))
    graph.add((conference, RDFS.label, Literal(presentation["name"])))
    graph.add((conference, OBO.BFO_0000051, invited_talk))
    graph.add((conference, BIBO.organizer, Literal(presentation["org"])))

    graph.add((invited_talk, RDF.type, VIVO.InvitedTalk))
    graph.add((invited_talk, RDFS.label, Literal(presentation["title"])))
    graph.add((invited_talk, VIVO.description, Literal(presentation["abstract"])))
    graph.add((invited_talk, VIVO.dateTimeInterval, datetime_interval))
    graph.add((invited_talk, OBO.BFO_0000050, conference))

    for num, person in enumerate(presentation.get("persons_involved")):
        person_id = person["id"]
        # we wish to exclude persons who are not uncw faculty
        # digitalmeasures gives non-uncw persons an empty string for an 'id'
        # so we check for empty 'id' and skip them
        if not person_id:
            continue
        person_elem = NS[person_id]
        other_attendee_role = NS[f"{presentation_id}b{num}"]
        graph.add((other_attendee_role, RDF.type, VIVO.AttendeeRole))
        graph.add((invited_talk, OBO.BFO_0000055, other_attendee_role))
        graph.add((other_attendee_role, OBO.BFO_0000054, invited_talk))
        graph.add((person_elem, OBO.RO_0000053, other_attendee_role))
        graph.add((other_attendee_role, OBO.RO_0000052, person_elem))
        graph.add((other_attendee_role, VIVO.dateTimeInterval, datetime_interval))

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


def add_intellcont_to_graph(graph, intellcont, fac):
    if intellcont.get("status") != "Published":
        return

    article_id = intellcont["id"]
    academic_article = NS[article_id]
    datetime_node = NS[f"{article_id}a"]
    journal = NS[f"{article_id}b"]

    publisher = intellcont["publisher"].strip()
    title = intellcont["title"].strip()
    abstract = intellcont.get("abstract").strip()
    doi = intellcont.get("doi").strip()
    volume = intellcont.get("volume").strip()
    issue = intellcont.get("issue").strip()
    date_published = intellcont.get("date_published").strip()
    page_nums = intellcont.get("page_nums").strip()
    startpage, endpage = split_pages(page_nums)
    content_type = map_contypes(intellcont.get("contype"))

    graph.add((journal, RDF.type, BIBO.Journal))
    graph.add((journal, RDFS.label, Literal(intellcont["publisher"])))
    graph.add((journal, VIVO.publicationVenueFor, academic_article))
    graph.add((academic_article, VIVO.hasPublicationVenue, journal))

    if date_published:
        graph.add((academic_article, VIVO.dateTimeValue, datetime_node))
        graph.add((datetime_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (
                datetime_node,
                VIVO.dateTime,
                Literal(intellcont["date_published"], datatype=XSD.date),
            )
        )
        graph.add((datetime_node, VIVO.dateTimePrecision, VIVO.yearPrecision))

    if content_type:
        graph.add((academic_article, RDF.type, content_type))
    if title:
        graph.add((academic_article, RDFS.label, Literal(title)))
    if abstract:
        graph.add((academic_article, BIBO.abstract, Literal(abstract)))
    if doi:
        graph.add((academic_article, BIBO.doi, Literal(doi)))
    if volume:
        graph.add((academic_article, BIBO.volume, Literal(volume)))
    if issue:
        graph.add((academic_article, BIBO.issue, Literal(issue)))
    if startpage:
        graph.add((academic_article, BIBO.pageStart, Literal(startpage)))
    if endpage:
        graph.add((academic_article, BIBO.pageEnd, Literal(endpage)))

    for num, person in enumerate(intellcont.get("persons_involved")):
        person_id = person["id"]
        # we wish to exclude persons who are not uncw faculty
        # digitalmeasures gives non-uncw persons an empty string for an 'id'
        # so we check for empty 'id' and skip them
        if not person_id:
            continue
        person_elem = NS[person_id]
        other_authorship = NS[f"{article_id}c{num}"]
        graph.add((other_authorship, RDF.type, VIVO.Authorship))
        graph.add((academic_article, VIVO.relatesBy, other_authorship))
        graph.add((other_authorship, VIVO.relates, academic_article))
        graph.add((person_elem, VIVO.relatedBy, other_authorship))
        graph.add((other_authorship, VIVO.relates, person_elem))


def add_perform_exhibit_to_graph(graph, perform_exhibit, fac):
    perf_id = perform_exhibit["id"]
    performance = NS[perf_id]
    conference = NS[f"{perf_id}a"]
    attendee_role = NS[f"{perf_id}b"]

    datetime_interval = NS[f"{perf_id}c"]
    time_start_node = NS[f"{perf_id}d"]
    time_end_node = NS[f"{perf_id}e"]

    graph.add((conference, RDF.type, BIBO.Conference))
    graph.add((conference, RDFS.label, Literal(perform_exhibit["name"])))
    graph.add((conference, OBO.BFO_0000051, performance))
    graph.add((conference, BIBO.organizer, Literal(perform_exhibit["sponsor"])))

    graph.add((performance, RDF.type, BIBO.Performance))
    graph.add((performance, RDFS.label, Literal(perform_exhibit["title"])))
    graph.add((performance, VIVO.description, Literal(perform_exhibit["desc"])))
    graph.add((performance, VIVO.dateTimeInterval, datetime_interval))
    graph.add((performance, OBO.BFO_0000050, conference))

    for num, person in enumerate(perform_exhibit.get("persons_involved")):
        person_id = person["id"]
        # we wish to exclude persons who are not uncw faculty
        # digitalmeasures gives non-uncw persons an empty string for an 'id'
        # so we check for empty 'id' and skip them
        if not person_id:
            continue
        person_elem = NS[person_id]
        other_attendee_role = NS[f"{perf_id}b{num}"]
        graph.add((other_attendee_role, RDF.type, VIVO.AttendeeRole))
        graph.add((performance, OBO.BFO_0000055, other_attendee_role))
        graph.add((other_attendee_role, OBO.BFO_0000054, performance))
        graph.add((person_elem, OBO.RO_0000053, other_attendee_role))
        graph.add((other_attendee_role, OBO.RO_0000052, person_elem))
        graph.add((other_attendee_role, VIVO.dateTimeInterval, datetime_interval))

    start_date = perform_exhibit["start_start"] or perform_exhibit["start_end"]
    end_date = perform_exhibit["end_start"] or perform_exhibit["end_end"]
    if start_date:
        graph.add((datetime_interval, RDF.type, VIVO.DateTimeInterval))
        graph.add((datetime_interval, VIVO.start, time_start_node))
        graph.add((time_start_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (time_start_node, VIVO.dateTime, Literal(start_date, datatype=XSD.date))
        )
        graph.add((time_start_node, VIVO.dateTimePrecision, VIVO.yearPrecision))
    if end_date:
        graph.add((datetime_interval, RDF.type, VIVO.DateTimeInterval))
        graph.add((datetime_interval, VIVO.end, time_end_node))
        graph.add((time_end_node, RDF.type, VIVO.DateTimeValue))
        graph.add((time_end_node, VIVO.dateTime, Literal(end_date, datatype=XSD.date)))
        graph.add((time_end_node, VIVO.dateTimePrecision, VIVO.yearPrecision))


def add_intellprop_to_graph(graph, intellprop):
    if intellprop["format"] != "Patent":
        return

    intellprop_id = intellprop["id"]
    intellprop_node = NS[intellprop_id]
    time_filed_node = NS[f"{intellprop_id}a"]
    time_issued_node = NS[f"{intellprop_id}b"]

    title = intellprop["title"].strip()
    patent_number = intellprop["id_number"]
    date_filed = intellprop["application_end"] or intellprop["application_start"]
    date_issued = intellprop["approve_end"] or intellprop["approve_start"]

    graph.add((intellprop_node, RDF.type, BIBO.Patent))
    if title:
        graph.add((intellprop_node, RDFS.label, Literal(title)))
    if patent_number:
        graph.add((intellprop_node, VIVO.patentNumber, Literal(patent_number)))
    if date_filed:
        graph.add((intellprop_node, VIVO.dateFiled, time_filed_node))
        graph.add((time_filed_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (time_filed_node, VIVO.dateTime, Literal(date_filed, datatype=XSD.date))
        )
        graph.add((time_filed_node, VIVO.dateTimePrecision, VIVO.yearPrecision))
    if date_issued:
        graph.add((intellprop_node, VIVO.dateIssued, time_issued_node))
        graph.add((time_issued_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (time_issued_node, VIVO.dateTime, Literal(date_issued, datatype=XSD.date))
        )
        graph.add((time_issued_node, VIVO.dateTimePrecision, VIVO.yearPrecision))

    for num, person in enumerate(intellprop["persons_involved"]):
        person_id = person["id"]
        # we wish to exclude persons who are not uncw faculty
        # digitalmeasures gives non-uncw persons an empty string for an 'id'
        # so we check for empty 'id' and skip them
        if not person_id:
            continue
        fac_node = NS[person_id]
        graph.add((intellprop_node, VIVO.assigneeFor, fac_node))
        graph.add((fac_node, VIVO.assignee, intellprop_node))


def add_congrant_to_graph(graph, congrant, user_id):
    if congrant["status"] not in {"Funded"}:
        return
    grant_id = congrant["id"]
    grant_node = NS[grant_id]
    time_filed_node = NS[f"{grant_id}a"]
    time_issued_node = NS[f"{grant_id}b"]
    funding_org_node = NS[f"{grant_id}c"]

    title = congrant["title"].strip()
    abstract = congrant["abstract"].strip()
    award_amount = congrant["amount"].strip()
    date_filed = congrant["sub_start"] or congrant["sub_end"]
    date_issued_start = congrant["start_start"] or congrant["start_end"]
    date_issued_end = congrant["end_start"] or congrant["end_end"]

    graph.add((grant_node, RDF.type, VIVO.Grant))
    if title:
        graph.add((grant_node, RDFS.label, Literal(title)))
    if abstract:
        graph.add((grant_node, BIBO.abstract, Literal(abstract)))
    if award_amount:
        graph.add((grant_node, VIVO.totalAwardAmount, Literal(award_amount)))

    if date_filed:
        graph.add((grant_node, VIVO.dateFiled, time_filed_node))
        graph.add((time_filed_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (time_filed_node, VIVO.dateTime, Literal(date_filed, datatype=XSD.date))
        )
        graph.add((time_filed_node, VIVO.dateTimePrecision, VIVO.yearPrecision))

    if date_issued_start or date_issued_end:
        date_issued_interval_node = NS[f"{grant_id}e"]
        date_issued_start_node = NS[f"{grant_id}f"]
        date_issued_end_node = NS[f"{grant_id}g"]

        graph.add((date_issued_interval_node, RDF.type, VIVO.DateTimeInterval))
        graph.add((date_issued_interval_node, VIVO.start, date_issued_start_node))
        graph.add((date_issued_interval_node, VIVO.end, date_issued_end_node))

        graph.add((date_issued_start_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (
                date_issued_start_node,
                VIVO.dateTime,
                Literal(date_issued_start, datatype=XSD.date),
            )
        )
        graph.add((date_issued_start_node, VIVO.dateTimePrecision, VIVO.yearPrecision))

        graph.add((date_issued_end_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (
                date_issued_end_node,
                VIVO.dateTime,
                Literal(date_issued_end, datatype=XSD.date),
            )
        )
        graph.add((date_issued_end_node, VIVO.dateTimePrecision, VIVO.yearPrecision))
        graph.add((grant_node, VIVO.dateTimeInterval, date_issued_interval_node))

    for num, person in enumerate(congrant["persons_involved"]):
        print(person)
        # Preventing investigator_nodes from clobbering or duplicating is hard when
        # each person's source file names the other investigators.  We prevent it
        # by only adding a node when grant person_id == the file's user_id.
        person_id = person["id"]
        if person_id != user_id:
            continue
        fac_node = NS[person_id]
        graph.add((grant_node, VIVO.relates, fac_node))
        graph.add((fac_node, VIVO.relatedBy, grant_node))
        # a unique investigator_node value for each pi role held by a person.
        random_num = ''.join(str(ord(i)) for i in person['lastname'])
        investigator_node = NS[f"{person_id}{grant_id}"]
        if person["role"] == "Principal":
            graph.add((investigator_node, RDF.type, VIVO.PrincipalInvestigatorRole))
        else:
            graph.add((investigator_node, RDF.type, VIVO.InvestigatorRole))
        graph.add((investigator_node, OBO.RO_0000052, fac_node))
        graph.add((fac_node, OBO.RO_0000053, investigator_node))
        graph.add((investigator_node, VIVO.relatedBy, grant_node))
        graph.add((grant_node, VIVO.relates, investigator_node))



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


def conjure_coll_dept_assignment(parsed_user):
    # Users are not entering accurate data.
    # There is no dept of Randall Library within the college of Business.
    # This magic wand is only necessary while the digitalmeasure data is incorrect.
    dmd_depts = parsed_user.get("current_depts")
    college_depts_info = [
        match_college(dept) for dept in dmd_depts if (dept and match_college(dept))
    ]
    return college_depts_info


def match_college(dept):
    # because users entered the wrong college for their dept in 10% of files
    # we have to assume they got the dept correct, and manually lookup the coll.
    # we also hardcoded the uid for college & for dept, for consistency
    for coll, bundle in COLL_DEPT.items():
        if dept in bundle.get("depts"):
            return {
                "coll_name": coll,
                "coll_uid": bundle["uid"],
                "dept_name": dept,
                "dept_uid": bundle["depts"][dept],
            }
    # if dept not in COLL_DEPT, check if it's in Academic Affairs
    if dept in ACADEMIC_AFFAIRS.get("depts"):
        return {
            "coll_name": ACADEMIC_AFFAIRS["name"],
            "coll_uid": ACADEMIC_AFFAIRS["uid"],
            "dept_name": dept,
            "dept_uid": ACADEMIC_AFFAIRS["depts"][dept],
        }
    return None


def split_pages(text):
    if not text:
        startpage, endpage = None, None
    elif "-" in text:
        startpage = text.split("-")[0].strip()
        endpage = text.split("-")[1].strip()
    else:
        startpage = text.strip()
        endpage = None
    return startpage, endpage


def map_contypes(contype):
    contypes_pubtypes = {
        None: BIBO.Document,
        "": BIBO.Document,
        "Book Review": BIBO.Document,
        "Book, Chapter in Non-Scholarly Book-New": BIBO.Chapter,
        "Book, Chapter in Non-Scholarly Book-Revised": BIBO.Chapter,
        "Book, Chapter in Scholarly Book-New": BIBO.Chapter,
        "Book, Chapter in Scholarly Book-Revised": BIBO.Chapter,
        "Book, Chapter in Textbook-New": BIBO.Chapter,
        "Book, Chapter in Textbook-Revised": BIBO.Chapter,
        "Book, Non-Scholarly-New": BIBO.Book,
        "Book, Non-Scholarly-Revised": BIBO.Book,
        "Book, Scholarly-New": BIBO.Book,
        "Book, Scholarly-Revised": BIBO.Book,
        "Book, Textbook-New": BIBO.Book,
        "Book, Textbook-Revised": BIBO.Book,
        "Broadcast Media": BIBO.AudioVisualDocument,
        "Cited Research": BIBO.Document,
        "Conference Proceeding": BIBO.ConferencePaper,
        "Instructor's Manual": BIBO.Manual,
        "Journal Article, Academic Journal": BIBO.AcademicArticle,
        "Journal Article, In-House Journal": BIBO.AcademicArticle,
        "Journal Article, Professional Journal": BIBO.AcademicArticle,
        "Journal Article, Public or Trade Journal": BIBO.AcademicArticle,
        "Law Review": BIBO.AcademicArticle,
        "Magazine/Trade Publication": BIBO.AcademicArticle,
        "Manuscript": BIBO.Manuscript,
        "Map": BIBO.Map,
        "Material Regarding New Courses/Curricula": BIBO.Document,
        "Monograph": BIBO.Document,
        "Newsletter": VIVO.Newsletter,
        "Newspaper": BIBO.Newspaper,
        "Nonfiction - Anthology": BIBO.Book,
        "Nonfiction - Book": BIBO.Book,
        "Nonfiction - Online Journal": BIBO.Article,
        "Nonfiction - Print Journal": BIBO.Article,
        "Novel": BIBO.Book,
        "Other": BIBO.Document,
        "Poetry - Anthology": BIBO.Document,
        "Poetry - Book": BIBO.Document,
        "Poetry - Online Journal": BIBO.Document,
        "Poetry - Print Journal": BIBO.Document,
        "Poster Session": VIVO.ConferencePoster,
        "Recording": BIBO.AudioVisualDocument,
        "Regular Column in Journal or Newspaper": BIBO.Article,
        "Research Report": BIBO.Report,
        "Short Fiction - Anthology": BIBO.Document,
        "Short Fiction - Book": BIBO.Document,
        "Short Fiction - Online Journal": BIBO.Document,
        "Short Fiction - Print Journal": BIBO.Document,
        "Software": OBO.ERO_0000071,
        "Software, Instructional": OBO.ERO_0000071,
        "Study Guide": BIBO.Document,
        "Technical Report": BIBO.Report,
        "Translation or Transcription": BIBO.Document,
        "Working Paper": VIVO.WorkingPaper,
        "Written Case with Instructional Material": BIBO.Document,
    }
    return contypes_pubtypes.get(contype)
