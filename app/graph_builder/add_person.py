from rdflib import Literal
from rdflib.namespace import RDF, RDFS

from globals import NS, OBO, VIVO, VCARD


def add_person_info_to_graph(graph, parsed_user):
    """
    fac is the person-as-employed -- Everything about a person that is tied to a job position.
    individual is the person-as-organism
    """
    user_id = parsed_user["userId"]
    fac = NS[user_id]
    individual = NS[f"{user_id}a"]
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


def add_personal_interests_to_graph(graph, parsed_user):
    user_id = parsed_user["userId"]
    fac = NS[user_id]
    bio = parsed_user["person"]["bio"]
    if bio:
        graph.add((fac, VIVO.overview, Literal(bio)))
    teaching_interests = parsed_user["person"]["teaching_interests"]
    if teaching_interests:
        graph.add((fac, VIVO.teachingOverview, Literal(teaching_interests)))
    research_interests = parsed_user["person"]["research_interests"]
    if research_interests:
        graph.add((fac, VIVO.researchOverview, Literal(research_interests)))
