from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO


def add_perform_exhibit_to_graph(graph, perform_exhibit, user_id):
    perf_id = perform_exhibit["id"]
    performance_node = NS[perf_id]
    conference = NS[f"{perf_id}a"]
    performer_node = NS[f"{perf_id}{user_id}"]

    datetime_interval = NS[f"{perf_id}c"]
    datetime_start = NS[f"{perf_id}d"]
    datetime_end = NS[f"{perf_id}e"]

    # add perform_exhibit["type"] somewhere.
    # also, the assignments may be incorrect

    graph.add((conference, RDF.type, BIBO.Conference))
    if perform_exhibit["name"]:
        graph.add((conference, RDFS.label, Literal(perform_exhibit["name"])))
    if perform_exhibit["sponsor"]:
        graph.add((conference, BIBO.organizer, Literal(perform_exhibit["sponsor"])))
    graph.add((conference, OBO.BFO_0000051, performance_node))
    graph.add((performance_node, OBO.BFO_0000050, conference))

    graph.add((performance_node, RDF.type, VIVO.Presentation))
    if perform_exhibit["title"]:
        graph.add((performance_node, RDFS.label, Literal(perform_exhibit["title"])))
    if perform_exhibit["desc"]:
        graph.add(
            (performance_node, VIVO.description, Literal(perform_exhibit["desc"]))
        )
    graph.add((performance_node, VIVO.dateTimeInterval, datetime_interval))

    for num, person in enumerate(perform_exhibit.get("persons_involved")):
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
        graph.add((performer_node, RDF.type, VIVO.PresenterRole))
        graph.add((performer_node, RDFS.label, Literal(person["role"])))
        graph.add((performer_node, VIVO.dateTimeInterval, datetime_interval))
        graph.add((performer_node, OBO.BFO_0000054, performance_node))
        graph.add((performance_node, OBO.BFO_0000055, performer_node))
        graph.add((performer_node, OBO.RO_0000052, fac_node))
        graph.add((fac_node, OBO.RO_0000053, performer_node))

    start_date = perform_exhibit["start_start"] or perform_exhibit["start_end"]
    end_date = perform_exhibit["end_start"] or perform_exhibit["end_end"]
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
