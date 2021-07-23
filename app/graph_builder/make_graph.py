import os
import rdflib

from globals import NS, OBO, VIVO, VCARD
from parse_userfiles import parse_userfile
from conjure_dept import conjure_coll_dept_assignment

from .add_orgs import add_orgs_to_graph
from .add_congrant import add_congrant_to_graph
from .add_presentation import add_presentation_to_graph
from .add_intellcont import add_intellcont_to_graph
from .add_perform_exhibit import add_perform_exhibit_to_graph
from .add_admin_assignment import add_admin_assignment_to_graph
from .add_intellprop import add_intellprop_to_graph
from .add_job_positions import add_job_positions_to_graph
from .add_person import add_person_info_to_graph, add_personal_interests_to_graph
from .add_profile_image import add_profile_image

# from .include_while_developing import include_while_developing


def make_graph(include_dir):
    graph = init_graph()
    add_orgs_to_graph(graph)

    for filename in sorted(os.listdir(include_dir)):
        # -- Development shortcircuit, to exclude most members --
        # username = os.path.split(filename)[0]
        # if not include_while_developing(username):
        #    continue
        filepath = os.path.join(include_dir, filename)
        parsed_user = parse_userfile(filepath)
        add_user_to_graph(graph, parsed_user)
    return graph


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
    add_profile_image(graph, user_id, fac_node)

    for admin_assignment in parsed_user["admin_assignments"]:
        add_admin_assignment_to_graph(graph, admin_assignment, fac, coll_dept_guess)
    for presentation in parsed_user["presentations"]:
        add_presentation_to_graph(graph, presentation, user_id)
    for intellcont in parsed_user["intellconts"]:
        add_intellcont_to_graph(graph, intellcont)
    for perform_exhibit in parsed_user["perform_exhibits"]:
        add_perform_exhibit_to_graph(graph, perform_exhibit, user_id)
    for intellprop in parsed_user["intellprops"]:
        add_intellprop_to_graph(graph, intellprop)
    for congrant in parsed_user["congrants"]:
        add_congrant_to_graph(graph, congrant, user_id)
