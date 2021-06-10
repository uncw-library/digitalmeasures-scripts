from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO


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
        # Preventing investigator_nodes from clobbering or duplicating is hard when
        # each person's source file names the other investigators.  We prevent it
        # by only adding a node when grant person_id == the file's user_id.
        person_id = person["id"]
        if person_id != user_id:
            continue

        fac_node = NS[person_id]
        graph.add((grant_node, VIVO.relates, fac_node))
        graph.add((fac_node, VIVO.relatedBy, grant_node))

        investigator_node = NS[f"{person_id}{grant_id}"]
        if person["role"] == "Principal":
            graph.add((investigator_node, RDF.type, VIVO.PrincipalInvestigatorRole))
        elif person["role"] == "Co-Principal":
            graph.add((investigator_node, RDF.type, VIVO.CoPrincipalInvestigatorRole))
        else:
            graph.add((investigator_node, RDF.type, VIVO.InvestigatorRole))

        graph.add((investigator_node, OBO.RO_0000052, fac_node))
        graph.add((fac_node, OBO.RO_0000053, investigator_node))
        graph.add((investigator_node, VIVO.relatedBy, grant_node))
        graph.add((grant_node, VIVO.relates, investigator_node))
