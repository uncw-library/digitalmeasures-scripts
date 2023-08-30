# globals.py

from rdflib import Namespace


NSMAP = {
    "a": "http://www.digitalmeasures.com/schema/data",
    "dmd": "http://www.digitalmeasures.com/schema/data-metadata",
}

NS = Namespace("http://scholars.uncw.edu/individual/")
BIBO = Namespace("http://purl.org/ontology/bibo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
VITRO = Namespace("http://vitro.mannlib.cornell.edu/ns/vitro/public#")

# The uids are arbitrary, but must not overlap with any uids from the source dataset.
# They also must remain unchanged across different runs of this script.
# Since this is a hard problem, I've manually selected some uid's from ADMIN_DEP elems in the source data
# because ADMIN_DEP uid's are not carried into the vivo import dataset
# but the ADMIN_DEP uid's are guarenteed to never equal a uid we may carry over.
# Essentially, trying to hardcode a uid that could never collide with another element's uid.
# Each org will need to change these uids.  I suggest using id values from the source ADMIN_DEP elements.

UNIVERSITY = {
    # same logic as COLL_DEPT regarding hardcoded uid
    "name": "University of North Carolina - Wilmington",
    "uid": "168540581888",
    "desc": "A description.",
}

ACADEMIC_AFFAIRS = {
    "name": "Academic Affairs",
    "uid": "168540397570",
    "desc": "A description",
    "depts": {
        "Randall Library": "161986105345",
        "Office of the Provost": "161986107393",
        "Office of the Graduate School": "161986109441",
        "Office of Center for Teaching Excellence & Center for Faculty Leadership": "161986111489",
        "Office of Diversity and Inclusion": "161986113537",
        "Office of the Dean, College of Arts and Sciences": "168541734913",
        "Office of International Programs": "161984303106",
        "Office of the Honors College": "14241826817",
        "Womens Resource Center": "161984301058",
        "Office of Undergraduate Studies": "161984296962",
        "Office of Cultural Arts": "161984299010",
    },
}

COLL_DEPT = {
    "Cameron School of Business": {
        "uid": "168540397569",
        "depts": {
            "Management": "168541353987",
            "Economics and Finance": "168541353984",
            "Office of the Dean, Cameron School of Business": "168541353986",
            "Business Analytics, Information Systems, and Supply Chain": "195135006723",
            "Accountancy and Business Law": "195135006722",
            "Marketing": "195135006721",
        },
    },
    "Chancellor's Office": {
        "uid": "195210027010",
        "depts": {
            "Office of the Chancellor": "195210027009",
            "Office of Diversity and Inclusion": "187931844609",
            "Office of Athletics": "195128840193",
        },
    },
    "College of Humanities, Social Sciences, and the Arts": {
        "uid": "195126493185",
        "depts": {
            "Anthropology": "161981390849",
            "Art and Art History": "161979498497",
            "Communication Studies": "168540702721",
            "Creative Writing": "161981396993",
            "English": "161984618498",
            "Film Studies": "161981405185",
            "History": "168541237249",
            "International Studies": "161981403137",
            "Music": "167971166209",
            "Philosophy and Religion": "161981407233",
            "Public and International Affairs": "161981392897",
            "Sociology and Criminology": "161981399041",
            "Theatre": "161984622594",
            "World Languages and Cultures": "161984616450",
            "Gender Studies & Research Center": "243941294081",
            "Graduate Liberal Studies": "24338143234",
            "Office of the Dean, College of Arts and Sciences": "161979746305",
        },
    },
    "College of Science and Engineering": {
        "uid": "14240530433",
        "depts": {
            "Biology and Marine Biology": "161984620546",
            "Chemistry and Biochemistry": "168541431810",
            "Computer Science": "161984614402",
            "Earth and Ocean Sciences": "161979500545",
            "Environmental Sciences": "161981401089",
            "Mathematics and Statistics": "161984612354",
            "Physics and Physical Oceanography": "161984610306",
            "Psychology": "161981394945",
            "Pre-Engineering": "239844139009",
            "Office of the Dean, College of Science and Engineering": "253325035521",
        },
    },
    "College of Health and Human Services": {
        "uid": "168540348417",
        "depts": {
            "School of Nursing": "161982855170",
            "School of Health and Applied Human Sciences": "161982857218",
            "School of Social Work": "161982859266",
            "Office of the Dean, College of Health and Human Services": "185862473729",
        },
    },
    "Watson College of Education": {
        "uid": "161982863362",
        "depts": {
            "Instructional Technology, Foundations, and Secondary Education": "161982865410",
            "Educational Leadership": "168541026306",
            "Early Childhood, Elementary, Middle, Literacy and Special Education": "161983545345",
            "Office of the Dean, Watson College of Education": "161983547393",
        },
    },
}
