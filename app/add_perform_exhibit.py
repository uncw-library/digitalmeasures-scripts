from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO


def add_perform_exhibit_to_graph(graph, perform_exhibit, user_id):
    perf_id = perform_exhibit["id"]
    performance = NS[perf_id]
    conference = NS[f"{perf_id}a"]
    attendee_role = NS[f"{perf_id}b"]

    datetime_interval = NS[f"{perf_id}c"]
    time_start_node = NS[f"{perf_id}d"]
    time_end_node = NS[f"{perf_id}e"]

    graph.add((conference, RDF.type, BIBO.Conference))
    graph.add((conference, RDFS.label, Literal(perform_exhibit["name"])))
    graph.add((conference, BIBO.organizer, Literal(perform_exhibit["sponsor"])))
    graph.add((conference, OBO.BFO_0000051, performance))
    graph.add((performance, OBO.BFO_0000050, conference))

    graph.add((performance, RDF.type, BIBO.Performance))
    graph.add((performance, RDFS.label, Literal(perform_exhibit["title"])))
    graph.add((performance, VIVO.description, Literal(perform_exhibit["desc"])))
    graph.add((performance, VIVO.dateTimeInterval, datetime_interval))

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
        other_attendee_role = NS[f"{perf_id}b{num}"]
        graph.add((performance, OBO.BFO_0000055, other_attendee_role))
        graph.add((other_attendee_role, OBO.BFO_0000054, performance))
        graph.add((other_attendee_role, RDF.type, VIVO.AttendeeRole))
        graph.add((other_attendee_role, VIVO.dateTimeInterval, datetime_interval))
        graph.add((other_attendee_role, OBO.RO_0000052, fac_node))
        graph.add((fac_node, OBO.RO_0000053, other_attendee_role))

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
