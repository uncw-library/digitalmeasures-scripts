from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO, VCARD


def add_job_positions_to_graph(graph, parsed_user, coll_dept_guess):
    user_id = parsed_user["userId"]
    fac = NS[user_id]
    individual = NS[f"{user_id}a"]
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
