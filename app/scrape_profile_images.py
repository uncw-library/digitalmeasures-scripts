import os


def scrape_profile_images():
    dest = os.path.join("output", "profile_images")
    os.makedirs(dest, exist_ok=True)
    pass
    # rest of code to locate the image & copy it to dest
