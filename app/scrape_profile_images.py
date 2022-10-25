import os
from smbclient import open_file

from parse_userfiles import parse_userfile


def scrape_profile_images(INCLUDE_DIR):
    for file in os.listdir(INCLUDE_DIR):
        scrape_image(os.path.join(INCLUDE_DIR, file))


def scrape_image(userfile):
    print(userfile)
    parsed = parse_userfile(userfile)
    if not parsed or not parsed.get('person'):
        return
    photo_url = parsed.get("person", {}).get("photo_url")
    userid = parsed.get("userId")
    print(type(photo_url), len(photo_url), photo_url, type(userid), len(userid), userid)
    can_proceed = photo_url and userid
    if not can_proceed:
        return
    photo = fetch_photo(photo_url, userid)
    if not photo:
        return
    write_main_image(photo, userid)
    write_thumb_image(photo, userid)


def fetch_photo(photo_url, userid, skip_existing=False):
    *dirs, filename = photo_url.split("/")
    source = "//itsdigmes01/digitalmeasuresdata/{}/{}".format("/".join(dirs), filename)
    username, password = os.getenv("DM_SAMBA_USER"), os.getenv("DM_SAMBA_PASS")
    try:
        with open_file(source, username=username, password=password, mode="rb") as fd:
            photo = fd.read()
    except:
        return None
    return photo


def write_main_image(photo, userid, skip_existing=False):
    # the tail matches what's in ./graph_builder/add_profile_images.py
    # '999' is the tail for main images & '333' for thumbnails
    threes = add_tail_and_break_into_threes(userid, "999")
    dest_path = f"output/image/a~n/{threes}"
    dest = f"{dest_path}/{userid}.jpg"
    os.makedirs(dest_path, exist_ok=True)
    if os.path.exists(dest) and skip_existing:
        return
    with open(dest, "wb") as f:
        f.write(photo)


def write_thumb_image(photo, userid, skip_existing=False):
    # the tail matches what's in ./graph_builder/add_profile_images.py
    # '999' is the tail for main images & '333' for thumbnails
    threes = add_tail_and_break_into_threes(userid, "333")
    dest_path = f"output/image/a~n/{threes}"
    dest = f"{dest_path}/thumbnail_{userid}.jpg"
    os.makedirs(dest_path, exist_ok=True)
    if os.path.exists(dest) and skip_existing:
        return
    with open(dest, "wb") as f:
        f.write(photo)


def add_tail_and_break_into_threes(userid, tail):
    # takes a '2345678' and returns a '234/567/899/9'
    # Vivo has these strange filepaths for uploaded photos
    with_tail = f"{userid}{tail}"
    path = ""
    for num, char in enumerate(with_tail):
        path += char
        if num % 3 == 2:
            path += "/"
    if path[-1] == "/":
        path = path[:-1]
    return path
