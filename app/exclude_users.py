# exclude_users.py

import json
import logging
import os

from scrape_directory import SeleniumDriver


GENERIC_USERS = {"facultytest"}
IRP = {"morristr"}
OFFICE_STAFF = {
    "armstrongg",
    "baileyj",
    "beaudoinh",
    "deltsi",
    "depompeisd",
    "grays",
    "hartmanc",
    "lindgrens",
    "mcdanielk",
    "murrayd",
    "ramadanik",
    "wrightlk",
    "helmsc",
    "smithzr",
    ""
}
NONFAC = {"sartarellij", "powells", "tirrelld", "ndoyea", "bullerss"}
NO_LONGER_WITH_UNCW = {"barriossosaa", "mininnis", "boldizarn", "kings", "brennerw", "aml3905", "cotellessad", "fernandezvillaj", "vickersk", "danielss", "bowengl", "depompeisd", "edwardsa", "ellispc", "glowas", "kawczynskib", "mcknightl", "paynesr", "treolod", "wilkinsonw", "wisemanc", "clarkt", "moorea", "canfieldm", "vegav1", "abioroe", "hca2343", "albrightm", "amersonk", "amponsahn", "andrewse", "ashtonc", "ema1750", "avidadarchilaa", "bastianic", "batchelorl", "beyere", "binghams", "bogdanoffa", "browderk", "bucklande", "buffingtond", "caseyj", "casterellag", "ejc3333", "cerezon", "chalkr", "chauvink", "chromanc", "chromanj", "ciokiewiczr", "coen", "collinst", "mnc2435", "courboisc", "cozzap", "crichtonm", "davrosn", "deetsj", "gattd", "diazs", "durringtonv", "eddyg", "enlowr", "ennekingk", "ericksone", "ewaldh", "fausts", "felisg", "fieldj", "foschiar", "gabrielj", "gadym", "garciaputnama", "gerardp", "glattj", "glennd", "gliddene", "gonkas", "grantn", "smithml", "grosseible", "rileygurganuss", "ag6645", "rmh7906", "hardinr", "harrisn", "jmf3265", "heinrichc", "hollenbeckf", "holts", "hoopesk", "houghtalenr", "hueberf", "hughesmc", "ibanezcasasi", "jacobsonj", "joneskg", "keelerd", "kelleyj", "kellsl", "kleppingerm", "wsk7547", "mbk3918", "kramerm", "lamaskint", "lancasterm", "mwl1084", "crl2516", "leacht", "leonardka", "leutzej", "livingstond", "ogl7251", "lowryb", "lukasl", "luptonq", "malcolmm", "markantonakisa", "mckinnoni", "mcnairys", "alr3720", "messnerm", "metcalfe", "metzgerj", "midgettey", "millerb", "millergl", "millerms", "mirabellaj", "nam1328", "mooneyhamd", "morgandc", "mutlua", "nelsonkt", "neumeyerx", "norrish", "oesterj", "lko5561", "oteror", "pappasa", "pearsonad", "pennar", "pentone", "powells", "rahala", "rakase", "ramirezm", "randallw", "rawitsche", "rescinom", "ker2684", "rheinsmiths", "richardsond", "robertsonh", "duernbergerk", "rowej", "ruffinba", "saccomanos", "cns4177", "cas7491", "les6953", "schellg", "schmittm", "schweizerc", "shankg", "shieldsd", "siegelr", "skippere", "smithhs", "smithlwa", "smithsma", "southerlyj", "stebbinsc", "stilesc", "stonesiferb", "straughns", "strohmierh", "strongj", "suttond", "swinsonh", "thompsonlw", "ept9216", "thurstond", "thurstont", "tt1108", "eat3538", "vandierdoncko", "varadir", "vossa", "wallacem1", "walstonl", "waltond", "warrena", "wattsad", "wepplerr", "mcl6280", "whitehm", "whitem", "wilburns", "williamsak", "wilsonse", "wirszylaj", "scw2109", "zamorap", "zeldina", "zibelink", "aliaa", "andersona", "ankrahl", "zna6187", "baileyc", "barberk", "barhama", "bassh", "seb1161", "bergh", "billingsleae", "bjorklundp", "boettcherg", "bongiornof", "borenm", "borkatakyvarmas", "bovel", "brandone", "icb8725", "GEB7124", "cappsf", "carrm", "carrollr", "chensj", "combsc", "conroye", "arc3031", "daileyj", "dawsond", "cdd7002", "deuschlec", "frd1988", "ellingtonk", "farinellajk", "faulknerm", "figueroaj", "fleminga", "sdf2042", "fosterj", "frankj", "srg9481", "gillaa", "girondaj", "gisolfim", "glassa", "glasss", "brg5926", "gomezguevarae", "goodwinc", "guarinom", "haneyc", "hansone", "hartss", "tth7050", "hathcocka", "cmi4355", "hillgramlischk", "hollandk", "howardc", "howe", "huckstadtl", "ikards", "irizarrye", "janzs", "kanoy", "rk3614", "kingd", "klined", "koesterj", "kolbea", "koszulinskig", "khk3381", "kroushln", "kruegerse", "lancelotj", "lanek", "edl6123", "lankfordt", "larsondm", "leemh", "lettmcgeev", "levandm", "linehant", "lynna", "madisonm", "manrossm", "cgm9612", "mautzrd", "mccoya", "mcgimseya", "mcneild", "meighenb", "emm5468", "milleta", "blm8639", "moraneh", "moranpr", "morrisjf", "morsem", "mrakn", "murdockn", "musserb", "nazarion", "nelsona", "nelsonms", "newlink", "noor", "okellow", "dho1053", "pabsta", "painterj", "parkerr", "perkinss", "phelpsa", "gnp3449", "pilgrimc", "pohlmank", "leasera", "powellaa", "pulliams", "ramper", "randolphl", "redar", "rhinehardtk", "rhodesdr", "richardsonm", "robertsonj", "robertsont", "rodgersk", "rogersar", "roylances", "salzmant", "schauerj", "schollenbergerk", "seahawk", "seatonp", "shpolbergm", "shumanj", "sillsv", "simmonssl", "simpsont", "sinclairs", "siriwardanac", "skeeter", "smithc", "snidera", "sperrys", "stallingsjl", "stallsj", "steenersonk", "sterrettw", "stids", "sullivanj", "summersb", "sundararajann", "swaffordj", "taggartj", "tracya", "trujilloj", "tuttlew", "vincenta", "wagnert", "watanabew", "welliverk", "whelanj", "tdw7471", "whitleya", "whitmerm", "wilkied", "wisen", "yatesj", "adamsjb", "adrianh", "ashleek", "askewk", "baileyk", "srb6481", "batesd", "beanj", "beltranl", "bemelmansk", "benderr", "boakyec", "boycer", "breedlovep", "hcb7809", "brownraa", "brudneyj", "brunsond", "bullerss", "byrdg", "campbellm", "cardamoned", "chaim", "corblissd", "covingtond", "fsc1829", "cgd6066", "donahoee", "dowdd", "dunnc", "durakom", "duranced", "fisherr", "forresterd", "franklinsl", "generousk", "gentrys", "gilla", "glandonh", "gloses", "lemonsr", "greata", "gurganusl", "haddadl", "handd", "hastingsm", "heistd", "heplerm", "herringp", "homere", "horowitzc", "hudsona", "huffmans", "huntsa", "reh5508", "kjj3419", "johnsonek", "jonesar", "kanek", "kapellj", "kilgorer", "kimh", "knudsong", "yak3182", "eal2090", "laursenc", "ledforda", "lettd", "lix", "limk", "lockhartz", "magnem", "mapesk", "markowskia", "mwm3448", "pdm1018", "sm2419", "merrittac", "akm9426", "millerdr", "mishoez", "mittals", "moldenk", "mulderr", "murrells", "nolandd", "nyea", "olsonv", "orrm", "grp5048", "cep6736", "vap1583", "map7186", "putnamg", "putneya", "rampea", "rapgayl", "reedym", "reynoldsew", "rotenbergj", "rowlandsc", "rudisillm", "ruwem", "sanchezm", "satterlier", "sawyer", "ejs5542", "shamblottk", "shifletts", "sokolofskyd", "spurdensa", "steine", "strussp", "swinsona", "tatej", "ct2458", "randall", "tetim", "turrisip", "upretyd", "usiltonl", "wadswortha", "wallacel", "warddr", "wengerj", "whitingm", "williamsjm", "wilsonhd", "jta7305", "adamsm", "agnirm", "cma8551", "askewjacksont", "ayalaa", "bachmeyerm", "baileyj", "battsk", "beachw", "beaudoinh", "kkb8567", "biggerstaffa", "bryantrichardse", "buchananl", "canipel", "coffeym", "comeauxp", "connolleyk", "kwc4497", "cunninghamj", "cunninghamo", "desth", "devitacochranec", "doddd", "ced7791", "knf1050", "fraserk", "mtf1072", "gabbarda", "cmg8439", "gillt", "greenel", "grossh", "guarinok", "hageee", "kal6656", "hallde", "harpers", "hartlinea", "hatleyl", "jbh7290", "hinese", "hoganw", "holmesw", "honchellb", "cmh1642", "aah6920", "irishc", "jacksonl", "jacobsp", "jettona", "joachimo", "joneslw", "kamenishp", "kigere", "kirkwoodc", "kirschkea", "koebelj", "kurtg", "lagrange", "leec", "nal8101", "dol4345", "rfm7537", "knm8222", "martinnb", "mcmurrays", "menonrm", "mingej", "morristr", "cmm6326", "oim8056", "nathansonr", "gigerj", "northrupv", "nunezs", "adamsoneilb", "olivolok", "oloiziaj", "awo4533", "bno5761", "ozierj", "pagehm", "palmern", "paparozzij", "parksl", "phillipsd", "pickensb", "jcp3677", "pucciom", "rackj", "reeves", "rhodesj", "ricej", "richardsons", "riverocalles", "ar4810", "rogersml", "rootl", "rushingw", "santaballas", "sawyersj", "shawj", "as8696", "smiths", "rss2157", "steadmane", "mms4333", "swartd", "tartep", "tompkinsj", "toomanq", "villeneuvee", "waitd", "walkerj", "warrenm", "wentworthm", "wertmans", "wetherillk", "whitek", "winslowh", "bfe7352", "zawistowskic", "zervosg", "aldemirj", "altobellos", "altrichterf", "andersonmr", "ia9256", "atwillw", "averettem", "msb3113", "badakhshd", "baden", "bageantk", "cb8217", "bakere", "bandarad", "bastan", "battenk", "lcb5495", "bergmanl", "berkeleya", "bevinsa", "ksb8482", "blejewskir", "blundor", "edb1708", "bourdelaisa", "bowenwefuanb", "bramanw", "bredbennerc", "cb9317", "brogdonl", "brophya", "brownln", "brunsonl", "burgesst", "bmc7374", "cantymitchellj", "capezzaj", "agc1323", "chakrabartys", "charlesk", "chinj", "clanceyj", "coatsl", "arc3902", "condonr", "conicellia", "conserw", "cottrellr", "coultera", "cowanb", "cmc3595", "clc4233", "cuttsl", "darrowe", "deltsi", "dentone", "devidor", "devriesc", "dorseyk", "dufordr", "eitelmans", "ellerbyj", "jse5258", "eversp", "facultytest", "faircloths", "feddersn", "fontanas", "fonviellec", "eef3807", "foxj", "frerem", "furiap", "gallaghers", "garrigaa", "garveyj", "gatesl", "gillespier", "gilliamc", "gosliney", "grahamn", "grays", "grobj", "gurganus", "hallj", "handlerb", "hardyk", "hardyp", "hartc", "helmsc", "hickmanj", "himesme", "hgh5720", "hoganph", "hollenbaughc", "honeycuttl", "iselina", "ivinst", "jacobsj", "janewl", "ksj8479", "jessend", "jonescm", "joneske", "junikur", "kaylorj", "keatingb", "kehayar", "kelleyp", "kernert", "kuiperr", "langh", "lapairep", "laws", "lewisat", "liw", "liaos", "lichtmanj", "longc", "lunsfordl", "lyonsk", "magliod", "malacinskit", "malmans", "marshalls", "martym", "mattocksn", "mccaffrays", "aem2784", "acm8905", "mcnamee", "mechlingl", "mendenhalln", "messingerl", "meyert", "alm2942", "millercle", "moallemm", "eam6445", "morenom", "morrisonj", "mfm3300", "murrayd", "pcn2556", "newberrym", "newelll", "novillom", "ogler", "opalkac", "overmanw", "overtonjd", "padillaa", "pembertona", "perryg", "snp6746", "picketts", "pottsa", "pottsl", "powelld", "pughl", "putnamj", "rabidouxs", "rankina", "registerl", "lr6369", "rheaumex", "rhudem", "robinsonc", "oar9914", "rosak", "plg4348", "rossb", "rosss", "rountreej", "bns7545", "ns3674", "salyardsg", "sandellk", "sartarellij", "sawrey", "bcs8898", "sayighl", "scalfm", "scarlettf", "scottmi", "secreastd", "crs4888", "pms3772", "sheridan", "sikoj", "cws4760", "ees6941", "smithja", "smithms", "smithzr", "snowdenl", "soukupj", "spradleyj", "staplesb", "stapletona", "stclairn", "stonec", "streeterm", "strongjd", "tagliarinig", "taylorjb", "tekulven", "thompsonb", "stt6153", "tomasc", "totha", "Vandergriffw", "mcw5893", "walbrechtm", "walkerb", "walkerr", "dow3346", "wayc", "jnw4992", "tkw4063", "whittingtona", "willeyj", "willis", "dgw1320", "wrightj", "yeagerv", "amz4211", "aktasf", "elikai", "hadselll", "herstinej", "wheelerj", "croweb", "fletcherr", "furnerz", "leonre", "longh", "nottinghamj", "rinconesr", "teitelbaumk", "tyndallre", "bermand", "buistc", "chaiml", "chenh", "crawfordr", "critesp", "dickensa", "faulknerg", "jonesjs", "kayay", "levyd", "lihua", "mahmoudr", "munozfd", "millerrk", "pattersone", "kay", "stairj", "venturaa", "whitlockc", "allingw", "andrewsk", "barcob", "bartht", "branders", "broadwellj", "burnettc", "chacec", "chlebnikd", "debuskg", "dillamanr", "dixont", "dluhym", "douglasa", "fettermanc", "gilleym", "gullettek", "hosier", "hossfeldl", "huberr", "kapraund", "kearnsp", "kyriacopoulosk", "lapierrem", "lerch", "longhl", "macdonaldb", "moorelj", "nezlekg", "potters", "pyotts", "roer", "rommels", "servickyl", "sizemorer", "szmanta", "tyrellj", "vantuinenm", "whitejw", "whitleyl", "avalosm", "bendera", "bennettj", "bowend", "brunaudvegav", "buergerp", "callahanc", "castellinol", "covane", "crowed", "dabundom", "dennison", "dennyj", "ennenk", "falsafin", "halld", "harrisjb", "hoggards", "hritzn", "huamanj", "johnstona", "keelinl", "kemppainenj", "kinneyt", "lawlessd", "levesquep", "livseyk", "mccannj", "nixj", "nordinb", "odonnells", "parkerv", "pollardd", "porterfieldr", "rasheedh", "reidn", "rinkaj", "savinonc", "sidmanc", "smithss", "violettek", "waldschlagelm", "whitfieldk", "zabriskiea", "belsera", "bowersjj", "ezzelld", "eeg7399", "jonesv", "pfohld", "riedingerk", "schuettpelze", "abramsl", "adamsp", "aguilaramuchasteguin", "akinleyej", "albergoc", "applefieldj", "ayersg", "ravij", "barlowc", "berkeleyk", "blasingamel", "bosen", "browna", "browne", "buckg", "buergerb", "buttinol", "byingtone", "carterd", "chambersj", "chapmanb", "chatzakise", "cilanoc", "clarka", "clarkl", "clavijo", "cliffordj", "codys", "colemanh", "connera", "cordled", "croomt", "cuttingr", "daviesm", "dennisc", "depaolo", "dipucciod", "farleye", "fellowsk", "fischettij", "fostere", "frierson", "gauthierc", "georgeb", "gogginsl", "sues", "gordonc", "gordont", "gouldc", "grindlayn", "hall", "harrisw", "hartmank", "hennigc", "henrye", "hernandezt", "huntleyl", "huntsmanj", "imigs", "irwind", "johnsonj", "johnstonl", "karlof", "kasalas", "kepleyh", "kims", "lacognataj", "lawson", "lemas", "lowery", "mahars", "mallalieul", "martinf", "martinn", "martins", "martinezm", "mccarthyw", "mccartneym", "mcmurrayn", "merrittj", "messers", "mitchells", "moorem", "moorewd", "mountj", "mountt", "moyerc", "myersj", "nices", "ongagak", "ortonc", "paarlbergl", "pavillb", "phelpsm", "reckb", "reinickeb", "robinsons", "rocknessh", "rocknessj", "rohlerl", "roscher", "rugoffk", "saksena", "seoj", "sepkoskid", "shafert", "brownrs", "shayl", "simmonssj", "slatenk", "smithd", "songb", "spackmank", "steelem", "suttonc", "tanp", "templed", "thayer", "thomascc", "thomasp", "thorntonc", "tremej", "veit", "vincentr", "wadmanw", "walbergg", "waltersk", "watsona", "watsteins", "wattsm", "waxmanb", "wheatb", "whitworthj", "wilkinsonc", "woodms", "ackermanc", "adamsv", "ainsleyf", "andersonju", "blacks", "chakarsj", "clearyw", "coxc", "crewsh", "lori.c.davis", "dionesotesm", "dockal", "earneyc", "evanst", "gillinghamp", "goodmana", "hanerfelda", "hel", "hurdled", "hurstr", "jarosinskij", "jenkinsw", "johnsonca", "maclennant", "mccall", "merrittt", "murphyj", "nesbitc", "richardsonj", "ritzhaupta", "rostampourf", "seask", "spikek", "tallantc", "walkerc", "ward", "watkinsa", "acunad", "adamsl", "adamswingate", "ainspacp", "akinleyeju", "allend", "allredr", "allredb", "alphina", "anglet", "aparicioc", "appletonb", "argenbrightr", "aselagem", "bagnellj", "baileys", "bairdr", "barnettef", "batchelorm", "beckab", "beechg", "bemelmansn", "benderk", "benzaquink", "berker", "berlinw", "bilgerm", "bomarp", "bombeldm", "bouls", "bowmanr", "boyajianm", "bradleym", "brewers", "brintonr", "broadwayw", "brownr", "brunjesj", "bruschip", "burkes", "cabbageb", "calhound", "campbellj", "campbellmo", "campbellr", "carpenters", "rcc6996", "catalfoj", "chakarsm", "chandlerg", "chandlerk", "chapmanf", "chappellp", "chesanowm", "childk", "civellij", "clarkg", "clarks", "colwellt", "cordlep", "coxj", "cracee", "davidj", "davisj", "decarvalhoc", "deratmiroffm", "desousaa", "dempseyd", "desorbot", "dorseys", "doshia", "elderm", "ellingtonm", "ellingtonrm", "elovaaram", "estesg", "estest", "expositow", "ferrelll", "fourqureand", "frisolia", "gaglianod", "garris", "glancyv", "glennb", "gormanr", "gouldk", "greeneac", "greicarm", "haasm", "hagleyr", "halljma", "hamiltont", "hayess", "haywoodr", "heglarc", "helsleym", "henryc", "hillk", "hoganp", "hollidayj", "hollingswort", "holmstedtk", "hortonn", "hulsea", "iklel", "irvine", "irwins", "ishamg", "ivonovm", "jacksona", "jacksonn", "jacocksh", "jarrellm", "jethroj", "jimenezm", "johnsonbs", "jonesh", "joneslc", "jonesp", "keenanl", "kinneyj", "koehlerr", "konradyh", "korte", "kravanjam", "krcmarb", "kreulj", "kwonm", "lambertjl", "laniers", "larsone", "lawinge", "lawsonc", "lawsong", "leeak", "lewispj", "lorieh", "luptont", "lutheranv", "mahlerr", "manockj", "mccalebe", "mccameyj", "mcgowanj", "mclamk", "mengy", "millerdk", "millerj", "millerm", "mintzes", "morris", "morrisonr", "murdocka", "murrayb", "murryw", "naarj", "nasutij", "ndoyea", "needhamr", "nelsonv", "noonanj", "norris", "nyec", "oakesp", "ohd", "olivolaj", "padgett", "padgettm", "paetzoldm", "parnellg", "pezzuolor", "phillipsw", "plataa", "poolem", "radomr", "ragazzok", "reada", "reidg", "griffinm", "richardsonw", "rickardj", "robbsm", "rogersp", "rosenmeierb", "rottmanna", "russella", "russellr", "ryand", "saunderse", "zvalarens", "shaferk", "shenkmanl", "sheparda", "shil", "sickelsa", "simmonsr", "simpsond", "skillmanj", "smallk", "smistj", "smitht", "smithdeall", "spearsg", "stallse", "starkk", "starrc", "steelegb", "steenersonc", "stonegordont", "stuggp", "sumnerb", "suttonr", "swearingene", "sweeneyp", "tatuml", "teacheyv", "theodoret", "thorpet", "tinklenbergm", "tobiasc", "toplinrb", "topore", "torokp", "townsendw", "trachtenbergp", "turnagee", "tyndallp", "vankirkm", "vanwagonerr", "veita", "vilarlopezr", "volip", "wanj", "warrenw", "watkinsk", "wattse", "webstere", "weddingtonh", "weedonr", "wichmannp", "widenerj", "williamsaw", "williamsl", "woodsw", "woodsiden", "woodulc", "yangx", "zuckermang", "barattac", "bealel", "masseyc", "mcgeea", "mcmurryj", "romanoj", "schneidermanj", "seiplej", "stokesj", "walterj", "watersj", "wellsj", "wilcoxl"}
OTHER_BAD_DATA = {"battenk"}

# Delete this variable when the API scraping bug is correctly recognizing hidden publications
TEMP_HIDDEN_PUBS_ARE_DISPLAYING = {'eshlemanm', 'sutterl', 'gambled', 'vetterr', 'chenyj', 'kamels', 'choij', 'kongy', 'irvinen', 'sardinaa', 'turrises', 'mcbrayerl', 'cardenasj', 'freudemana', 'monahand', 'rigginsa', 'sellonm', 'framptona', 'kerrj', 'yopakk', 'porcoa'}

FORCE_EXCLUDE = set().union(GENERIC_USERS, OFFICE_STAFF, IRP, NONFAC, NO_LONGER_WITH_UNCW, OTHER_BAD_DATA, TEMP_HIDDEN_PUBS_ARE_DISPLAYING)

FORCE_INCLUDE = {"crowes", "fritzlerp", "saundersn"}


def remove_excluded_users(parsed_users_dir):
    selenium_driver = SeleniumDriver()
    all_filenames = sorted(os.listdir(parsed_users_dir))
    for filename in all_filenames:
        if is_exclude(parsed_users_dir, filename, selenium_driver):
            os.remove(os.path.join(parsed_users_dir, filename))
            print(f"removed {filename}")
    selenium_driver.driver.quit()
    logging.info("removed excluded users from parsed_users dir")


def is_exclude(parsed_users_dir, filename, selenium_driver):
    filepath = os.path.join(parsed_users_dir, filename)
    with open(filepath, "r") as f:
        parsed_user = json.load(f)

    if not parsed_user:
        return True
    if is_force_include(parsed_user):
        return False
    if is_force_exclude(parsed_user):
        return True
    if is_only_do_not_use(parsed_user):
        return True
    if is_student(parsed_user):
        return True
    if not is_in_directory(parsed_user, selenium_driver):
        return True

    return False


def is_force_include(parsed_user):
    if parsed_user.get("username") in FORCE_INCLUDE:
        return True
    return False


def is_force_exclude(parsed_user):
    if parsed_user.get("username") in FORCE_EXCLUDE:
        return True
    return False


def is_only_do_not_use(parsed_user):
    # some users have a department name with the text "DO NOT USE".
    # exclude the user if all their departments names are such.
    listed_depts = [dept for dept in parsed_user.get("current_depts") if dept]
    minus_do_not_use_depts = [
        dept
        for dept in parsed_user.get("current_depts")
        if dept and "do not use" not in dept.lower()
    ]
    if len(listed_depts) != len(minus_do_not_use_depts):
        return True
    return False


def is_student(parsed_user):
    username = parsed_user.get("username")
    if username[-4:].isnumeric():
        return True
    return False


def is_in_directory(parsed_user, selenium_driver):
    # directory requires each namepart have 2+ characters.
    # someone with short lastname can't be found.
    # same for some one with short firstname.
    # Erring on the side of including those with short names.

    try:
        firstname = parsed_user.get("person").get("firstname")
    except AttributeError:
        firstname = None
    if not firstname or len(firstname) < 2:
        return True

    try:
        lastname = parsed_user.get("person").get("lastname")
    except AttributeError:
        lastname = None
    if not lastname or len(lastname) < 2:
        return True

    directory_results = selenium_driver.lookup_directory(
        firstname=firstname, lastname=lastname
    )
    if not directory_results:
        return False

    return True
