import os

from parse_userfiles import parse_userfile


def scrape_profile_images(USERFILES_DIR, PERSON_IMAGES_DIR):
    for file in os.listdir(USERFILES_DIR):
        scrape_image(os.path.join(USERFILES_DIR, file))
        # rest of code to locate the image & copy it to dest


def scrape_image(userfile):
    parsed = parse_userfile(userfile)
    # photo_identifier = parsed['some_identifier']
    # scrape photo from somewhere
    # put photo in PERSON_IMAGES_DIR/nnn/nnn/nn9/99/nnnnnnnn.jpg as vivo file_storage_root expects
    # make thumbnail image
    # put thumbnail in PERSON_IMAGES_DIR/nnn/nnn/nn3/33/nnnnnnnn.jpg
