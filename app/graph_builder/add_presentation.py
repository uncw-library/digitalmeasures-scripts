from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO


def add_presentation_to_graph(graph, presentation, user_id):
    presentation_id = presentation["id"]
    presentation_node = NS[presentation_id]
    conference = NS[f"{presentation_id}a"]
    presenter_node = NS[f"{presentation_id}b"]

    datetime_interval = NS[f"{presentation_id}c"]
    datetime_start = NS[f"{presentation_id}d"]
    datetime_end = NS[f"{presentation_id}e"]

    graph.add((conference, RDF.type, BIBO.Conference))
    graph.add((conference, RDFS.label, Literal(presentation["name"])))
    graph.add((conference, BIBO.organizer, Literal(presentation["org"])))
    graph.add((conference, OBO.BFO_0000051, presentation_node))
    graph.add((presentation_node, OBO.BFO_0000050, conference))

    graph.add((presentation_node, RDF.type, VIVO.Presentation))
    graph.add((presentation_node, RDFS.label, Literal(presentation["title"])))
    graph.add((presentation_node, VIVO.description, Literal(presentation["abstract"])))
    graph.add((presentation_node, VIVO.dateTimeInterval, datetime_interval))

    for person in presentation.get("persons_involved"):
        person_id = person["id"]
        fac_node = NS[person_id]
        # Preventing presenter nodes from clobbering or duplicating is hard when
        # each person's source file names the other presenters.  We prevent it
        # by only adding a node when presentation person_id == the file's user_id.
        if person_id != user_id:
            continue
        # we wish to exclude persons who are not uncw faculty
        # digitalmeasures gives non-uncw persons an empty string for an 'id'
        # so we check for empty 'id' and skip them
        if not person_id:
            continue
        graph.add((presenter_node, RDF.type, VIVO.PresenterRole))
        # graph.add((presenter_node, RDFS.label, Literal(person["role"])))
        graph.add((presenter_node, VIVO.dateTimeInterval, datetime_interval))
        graph.add((presenter_node, OBO.BFO_0000054, presentation_node))
        graph.add((presentation_node, OBO.BFO_0000055, presenter_node))
        graph.add((presenter_node, OBO.RO_0000052, fac_node))
        graph.add((fac_node, OBO.RO_0000053, presenter_node))

    start_date = presentation["date_start"]
    end_date = presentation["date_end"]
    if start_date:
        graph.add((datetime_interval, RDF.type, VIVO.DateTimeInterval))
        graph.add((datetime_interval, VIVO.start, datetime_start))
        graph.add((datetime_start, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (datetime_start, VIVO.dateTime, Literal(start_date, datatype=XSD.date))
        )
        graph.add((datetime_start, VIVO.dateTimePrecision, VIVO.yearPrecision))
    if end_date:
        graph.add((datetime_interval, RDF.type, VIVO.DateTimeInterval))
        graph.add((datetime_interval, VIVO.end, datetime_end))
        graph.add((datetime_end, RDF.type, VIVO.DateTimeValue))
        graph.add((datetime_end, VIVO.dateTime, Literal(end_date, datatype=XSD.date)))
        graph.add((datetime_end, VIVO.dateTimePrecision, VIVO.yearPrecision))
