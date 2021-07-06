def include_while_developing(username):
    if has_coauthor(username):
        return True
    if has_PERFORM_EXHIBIT(username):
        return True
    if has_PRESENT(username):
        return True
    if has_INTELLPROP(username):
        return True
    if has_CONGRANT(username):
        return True
    if has_BIO(username):
        return True
    if has_active_ADMIN_ASSIGNMENTS(username):
        return True
    if has_mismatched_titles(username):
        return True
    return False


def has_coauthor(username):
    # With co-authors
    if username in (
        "ahernn",
        "falsafin",
        "mechlingb",
        "waldschlagelm",
        "devitaj",
        "kolomers",
        "palumbor",
        "leej",
    ):
        return True
    return False


def has_PERFORM_EXHIBIT(username):
    if username in (
        "cordied",
        "cordiep",
        "degennarod",
        "errantes",
        "furiap",
        "haddadl",
        "kaylorj",
        "kingn",
        "waddellm",
        "ainspacp",
    ):
        return True
    return False


def has_PRESENT(username):
    if username in ("covij", "rocknessh", "seidmanm", "devitacochranec", "sackleyw"):
        return True
    return False


def has_INTELLPROP(username):
    if username in ("baden", "carrm", "changy"):
        return True
    return False


def has_CONGRANT(username):
    if username in ("turrises", "bovel", "carrollr"):
        return True
    return False


def has_BIO(username):
    if username in ("struckelle",):
        return True
    return False


def has_mismatched_titles(username):
    if username in ("schnorrc", "andrewsm", "bergh", "biehnerb"):
        return True
    return False


def has_active_ADMIN_ASSIGNMENTS(username):
    if username in ("ahernn", "chandlerb", "cathorallm", "calhound", "buffingtond"):
        return True
    return False
