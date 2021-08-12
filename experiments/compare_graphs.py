import argparse

from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff


def make_graph(filepath):
    g = Graph()
    g.parse(filepath, format="n3")
    return g


def compare_graphs(graphs):
    iso1, iso2 = [to_isomorphic(i) for i in graphs]
    if iso1 == iso2:
        print("same graph")
        exit()
    else:
        print("different")
        in_both, in_first, in_second = graph_diff(iso1, iso2)
        print(f"in first:\n {dump_nt_sorted(in_first)}\n\n")
        print(f"in second:\n {dump_nt_sorted(in_second)}\n\n")


def dump_nt_sorted(g):
    return [
        l.decode("utf-8") for l in sorted(g.serialize(format="n3").splitlines()) if l
    ]


def parse_args():
    parser = argparse.ArgumentParser(description="Specify files")
    parser.add_argument("filepaths", type=str, help="files to compare", nargs=2)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    graphs = [make_graph(i) for i in args.filepaths]
    compare_graphs(graphs)
