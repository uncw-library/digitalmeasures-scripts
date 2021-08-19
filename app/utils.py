import io
import logging
import os
import argparse


def setup_logging(APP_ROOT):
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    logging.basicConfig(
        filename=os.path.join(APP_ROOT, "log.txt"),
        level=logging.INFO,
        format="%(asctime)s: %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging_string = io.StringIO()
    string_handler = logging.StreamHandler(logging_string)
    string_handler.setLevel(logging.DEBUG)
    string_handler.setFormatter(formatter)
    logging.getLogger("").addHandler(string_handler)
    return logging_string


def parse_args():
    parser = argparse.ArgumentParser(
        description="fetch digitalmeasure and convert into turtle"
    )
    parser.add_argument(
        "--no_reset",
        action='store_true',
        default=argparse.SUPPRESS,
        help="prevents full reset of dm data (dev use)"
    )
    args = parser.parse_args()
    return args