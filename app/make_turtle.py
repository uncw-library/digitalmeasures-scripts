# make_turtle.py

import rdflib

from globals import NS, OBO, VIVO, VCARD
from globals import ACADEMIC_AFFAIRS, COLL_DEPT

from add_congrant import add_congrant_to_graph
from add_presentation import add_presentation_to_graph
from add_intellcont import add_intellcont_to_graph
from add_perform_exhibit import add_perform_exhibit_to_graph
from add_admin_assignment import add_admin_assignment_to_graph
from add_intellprop import add_intellprop_to_graph
from add_job_positions import add_job_positions_to_graph
from add_person import add_person_info_to_graph, add_personal_interests_to_graph


def init_graph():
    graph = rdflib.Graph()
    graph.namespace_manager.bind("vivo", VIVO, override=False)
    graph.namespace_manager.bind("vcard", VCARD, override=False)
    graph.namespace_manager.bind("obo", OBO, override=False)
    return graph


def add_user_to_graph(graph, parsed_user):
    user_id = parsed_user["userId"]
    fac = NS[user_id]
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

    add_person_info_to_graph(graph, parsed_user)
    add_personal_interests_to_graph(graph, parsed_user)
    add_job_positions_to_graph(graph, parsed_user, coll_dept_guess)

    for admin_assignment in parsed_user["admin_assignments"]:
        add_admin_assignment_to_graph(graph, admin_assignment, fac, coll_dept_guess)
    for presentation in parsed_user["presentations"]:
        add_presentation_to_graph(graph, presentation, user_id)
    for intellcont in parsed_user["intellconts"]:
        add_intellcont_to_graph(graph, intellcont, fac)
    for perform_exhibit in parsed_user["perform_exhibits"]:
        add_perform_exhibit_to_graph(graph, perform_exhibit, user_id)
    for intellprop in parsed_user["intellprops"]:
        add_intellprop_to_graph(graph, intellprop)
    for congrant in parsed_user["congrants"]:
        add_congrant_to_graph(graph, congrant, user_id)


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
