import json
import os

from smbclient import open_file


def scrape_profile_images(PARSED_USERS_DIR, PERSON_IMAGES_DIR):
    for file in os.listdir(PARSED_USERS_DIR):
        filepath = os.path.join(PARSED_USERS_DIR, file)
        with open(filepath, "r") as f:
            parsed_user = json.load(f)
        scrape_succeeded = scrape_image(parsed_user, PERSON_IMAGES_DIR)
        add_photo_metadata(filepath, parsed_user, scrape_succeeded)


def scrape_image(parsed_user, PERSON_IMAGES_DIR):
    if not has_image_info(parsed_user):
        return False
    photo_url = parsed_user.get("person", {}).get("photo_url")
    userid = parsed_user.get("userId")
    photo = fetch_photo(photo_url, userid)
    if not photo:
        return False
    write_main_image(photo, userid, PERSON_IMAGES_DIR)
    write_thumb_image(photo, userid, PERSON_IMAGES_DIR)
    return True


def has_image_info(parsed_user):
    if not parsed_user:
        return False
    if not parsed_user.get("userId"):
        return False
    if not parsed_user.get("person"):
        return False
    if not parsed_user.get("person", {}).get("photo_url"):
        return False
    return True


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


def write_main_image(photo, userid, PERSON_IMAGES_DIR):
    # the tail matches what's in ./graph_builder/add_profile_images.py
    # '999' is the tail for main images & '333' for thumbnails
    threes = add_tail_and_break_into_threes(userid, "999")
    dest_path = f"{PERSON_IMAGES_DIR}/a~n/{threes}"
    dest = f"{dest_path}/{userid}.jpg"
    os.makedirs(dest_path, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(photo)


def write_thumb_image(photo, userid, PERSON_IMAGES_DIR):
    # the tail matches what's in ./graph_builder/add_profile_images.py
    # '999' is the tail for main images & '333' for thumbnails
    threes = add_tail_and_break_into_threes(userid, "333")
    dest_path = f"{PERSON_IMAGES_DIR}/a~n/{threes}"
    dest = f"{dest_path}/thumbnail_{userid}.jpg"
    os.makedirs(dest_path, exist_ok=True)
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


def add_photo_metadata(filepath, parsed_user, scrape_succeeded):
    if not parsed_user.get("local_metadata"):
        parsed_user["local_metadata"] = dict()
    parsed_user["local_metadata"]["image_scrape_succeeded"] = scrape_succeeded
    json_text = json.dumps(parsed_user, indent=2, sort_keys=True)
    with open(filepath, "w") as f:
        f.write(json_text)
