from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, VIVO


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
