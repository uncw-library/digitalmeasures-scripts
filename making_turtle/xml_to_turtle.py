#!/usr/bin/env python
# xml_to_turtle.py

import os


from exclude_users import preignored_users, is_excluded_user
from make_turtle import init_graph, add_orgs_to_graph, add_user_to_graph
from parse_userfiles import parse_userfile
from scrape_directory import driver


if __name__ == "__main__":
    graph = init_graph()
    add_orgs_to_graph(graph)

    driver = driver

    for filename in sorted(os.listdir("../extracting/output/users/")):
        if filename not in (
            "ahernn.xml",
            "falsafin.xml",
            "mechlingb.xml",
            "waldschlagelm.xml",
            "devitaj.xml",
            "kolomers.xml",
            "palumbor.xml",
            "leej.xml",
        ):
            continue
        if filename.split(".")[0] in preignored_users:
            continue
        parsed_user = parse_userfile(f"../extracting/output/users/{filename}")
        if is_excluded_user(parsed_user, driver):
            continue
        add_user_to_graph(parsed_user, graph)
    driver.close()

    filetext = graph.serialize(format="turtle").decode("utf-8")
    with open("all.ttl", "w") as f:
        f.write(filetext)
