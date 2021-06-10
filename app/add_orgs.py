from rdflib import Literal
from rdflib.namespace import RDF, RDFS

from globals import NS, OBO, VIVO
from globals import UNIVERSITY, ACADEMIC_AFFAIRS, COLL_DEPT


def add_orgs_to_graph(graph):
    # Our organization structure is University->Division->College->AcademicDepartment
    univ_elem = NS[UNIVERSITY["uid"]]
    graph.add((univ_elem, RDF.type, VIVO.University))
    graph.add((univ_elem, RDFS.label, Literal(UNIVERSITY["name"])))
    graph.add((univ_elem, VIVO.overview, Literal(UNIVERSITY["desc"])))

    division_elem = NS[ACADEMIC_AFFAIRS["uid"]]
    graph.add((division_elem, RDF.type, VIVO.Division))
    graph.add((division_elem, RDFS.label, Literal(ACADEMIC_AFFAIRS["name"])))
    graph.add((division_elem, VIVO.overview, Literal(ACADEMIC_AFFAIRS["desc"])))
    graph.add((univ_elem, OBO.BFO_0000051, division_elem))
    graph.add((division_elem, OBO.BFO_0000050, univ_elem))

    for dept_name, dept_uid in ACADEMIC_AFFAIRS["depts"].items():
        dept_elem = NS[dept_uid]
        graph.add((dept_elem, RDF.type, VIVO.AcademicDepartment))
        graph.add((dept_elem, RDFS.label, Literal(dept_name)))
        graph.add((dept_elem, OBO.BFO_0000050, division_elem))
        graph.add((division_elem, OBO.BFO_0000051, dept_elem))

    for coll, coll_details in COLL_DEPT.items():
        coll_elem = NS[coll_details["uid"]]
        graph.add((coll_elem, RDF.type, VIVO.College))
        graph.add((division_elem, OBO.BFO_0000051, coll_elem))
        graph.add((coll_elem, OBO.BFO_0000050, division_elem))
        graph.add((coll_elem, RDFS.label, Literal(coll)))

        for dept_name, dept_uid in coll_details["depts"].items():
            dept_elem = NS[dept_uid]
            graph.add((dept_elem, RDF.type, VIVO.AcademicDepartment))
            graph.add((dept_elem, RDFS.label, Literal(dept_name)))
            graph.add((dept_elem, OBO.BFO_0000050, coll_elem))
            graph.add((coll_elem, OBO.BFO_0000051, dept_elem))
