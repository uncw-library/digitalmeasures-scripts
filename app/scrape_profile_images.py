import os

from parse_userfiles import parse_userfile

def scrape_profile_images(USERFILES_DIR, PERSON_IMAGES_DIR):
    os.makedirs(PERSON_IMAGES_DIR, exist_ok=True)
    for file in os.listdir(USERFILES_DIR):
        scrape_image(os.path.join(USERFILES_DIR, file))
        # rest of code to locate the image & copy it to dest


def scrape_image(userfile):
    parsed = parse_userfile(userfile)
    # photo_identifier = parsed['some_identifier']
    # scrape photo from somewhere
    # put photo in PERSON_IMAGES_DIR
    # possibly split filepath in /nnn/nnn/nn/filename.jpg as vivo file_storage_root expects
