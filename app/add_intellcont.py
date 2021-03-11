from rdflib import Literal
from rdflib.namespace import RDF, RDFS, XSD

from globals import NS, BIBO, OBO, VIVO


def add_intellcont_to_graph(graph, intellcont, fac):
    if intellcont.get("status") != "Published":
        return

    article_id = intellcont["id"]
    academic_article = NS[article_id]
    datetime_node = NS[f"{article_id}a"]
    journal = NS[f"{article_id}b"]

    publisher = intellcont["publisher"].strip()
    title = intellcont["title"].strip()
    abstract = intellcont.get("abstract").strip()
    doi = intellcont.get("doi").strip()
    volume = intellcont.get("volume").strip()
    issue = intellcont.get("issue").strip()
    date_published = intellcont.get("date_published").strip()
    page_nums = intellcont.get("page_nums").strip()
    startpage, endpage = split_pages(page_nums)
    content_type = map_contypes(intellcont.get("contype"))

    graph.add((journal, RDF.type, BIBO.Journal))
    graph.add((journal, RDFS.label, Literal(intellcont["publisher"])))
    graph.add((journal, VIVO.publicationVenueFor, academic_article))
    graph.add((academic_article, VIVO.hasPublicationVenue, journal))

    if date_published:
        graph.add((academic_article, VIVO.dateTimeValue, datetime_node))
        graph.add((datetime_node, RDF.type, VIVO.DateTimeValue))
        graph.add(
            (
                datetime_node,
                VIVO.dateTime,
                Literal(intellcont["date_published"], datatype=XSD.date),
            )
        )
        graph.add((datetime_node, VIVO.dateTimePrecision, VIVO.yearPrecision))

    if content_type:
        graph.add((academic_article, RDF.type, content_type))
    if title:
        graph.add((academic_article, RDFS.label, Literal(title)))
    if abstract:
        graph.add((academic_article, BIBO.abstract, Literal(abstract)))
    if doi:
        graph.add((academic_article, BIBO.doi, Literal(doi)))
    if volume:
        graph.add((academic_article, BIBO.volume, Literal(volume)))
    if issue:
        graph.add((academic_article, BIBO.issue, Literal(issue)))
    if startpage:
        graph.add((academic_article, BIBO.pageStart, Literal(startpage)))
    if endpage:
        graph.add((academic_article, BIBO.pageEnd, Literal(endpage)))

    for num, person in enumerate(intellcont.get("persons_involved")):
        person_id = person["id"]
        # we wish to exclude persons who are not uncw faculty
        # digitalmeasures gives non-uncw persons an empty string for an 'id'
        # so we check for empty 'id' and skip them
        if not person_id:
            continue
        person_elem = NS[person_id]
        other_authorship = NS[f"{article_id}c{num}"]
        graph.add((other_authorship, RDF.type, VIVO.Authorship))
        graph.add((academic_article, VIVO.relatesBy, other_authorship))
        graph.add((other_authorship, VIVO.relates, academic_article))
        graph.add((person_elem, VIVO.relatedBy, other_authorship))
        graph.add((other_authorship, VIVO.relates, person_elem))


def map_contypes(contype):
    contypes_pubtypes = {
        None: BIBO.Document,
        "": BIBO.Document,
        "Book Review": BIBO.Document,
        "Book, Chapter in Non-Scholarly Book-New": BIBO.Chapter,
        "Book, Chapter in Non-Scholarly Book-Revised": BIBO.Chapter,
        "Book, Chapter in Scholarly Book-New": BIBO.Chapter,
        "Book, Chapter in Scholarly Book-Revised": BIBO.Chapter,
        "Book, Chapter in Textbook-New": BIBO.Chapter,
        "Book, Chapter in Textbook-Revised": BIBO.Chapter,
        "Book, Non-Scholarly-New": BIBO.Book,
        "Book, Non-Scholarly-Revised": BIBO.Book,
        "Book, Scholarly-New": BIBO.Book,
        "Book, Scholarly-Revised": BIBO.Book,
        "Book, Textbook-New": BIBO.Book,
        "Book, Textbook-Revised": BIBO.Book,
        "Broadcast Media": BIBO.AudioVisualDocument,
        "Cited Research": BIBO.Document,
        "Conference Proceeding": BIBO.ConferencePaper,
        "Instructor's Manual": BIBO.Manual,
        "Journal Article, Academic Journal": BIBO.AcademicArticle,
        "Journal Article, In-House Journal": BIBO.AcademicArticle,
        "Journal Article, Professional Journal": BIBO.AcademicArticle,
        "Journal Article, Public or Trade Journal": BIBO.AcademicArticle,
        "Law Review": BIBO.AcademicArticle,
        "Magazine/Trade Publication": BIBO.AcademicArticle,
        "Manuscript": BIBO.Manuscript,
        "Map": BIBO.Map,
        "Material Regarding New Courses/Curricula": BIBO.Document,
        "Monograph": BIBO.Document,
        "Newsletter": VIVO.Newsletter,
        "Newspaper": BIBO.Newspaper,
        "Nonfiction - Anthology": BIBO.Book,
        "Nonfiction - Book": BIBO.Book,
        "Nonfiction - Online Journal": BIBO.Article,
        "Nonfiction - Print Journal": BIBO.Article,
        "Novel": BIBO.Book,
        "Other": BIBO.Document,
        "Poetry - Anthology": BIBO.Document,
        "Poetry - Book": BIBO.Document,
        "Poetry - Online Journal": BIBO.Document,
        "Poetry - Print Journal": BIBO.Document,
        "Poster Session": VIVO.ConferencePoster,
        "Recording": BIBO.AudioVisualDocument,
        "Regular Column in Journal or Newspaper": BIBO.Article,
        "Research Report": BIBO.Report,
        "Short Fiction - Anthology": BIBO.Document,
        "Short Fiction - Book": BIBO.Document,
        "Short Fiction - Online Journal": BIBO.Document,
        "Short Fiction - Print Journal": BIBO.Document,
        "Software": OBO.ERO_0000071,
        "Software, Instructional": OBO.ERO_0000071,
        "Study Guide": BIBO.Document,
        "Technical Report": BIBO.Report,
        "Translation or Transcription": BIBO.Document,
        "Working Paper": VIVO.WorkingPaper,
        "Written Case with Instructional Material": BIBO.Document,
    }
    return contypes_pubtypes.get(contype)


def split_pages(text):
    if not text:
        startpage, endpage = None, None
    elif "-" in text:
        startpage = text.split("-")[0].strip()
        endpage = text.split("-")[1].strip()
    else:
        startpage = text.strip()
        endpage = None
    return startpage, endpage
