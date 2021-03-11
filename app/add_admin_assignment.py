from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, VIVO


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
