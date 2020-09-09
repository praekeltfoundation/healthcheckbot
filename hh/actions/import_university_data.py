import csv
import sys
from collections import defaultdict

from ruamel.yaml import YAML

PROVINCE_MAPPING = {
    "EC": "ec",
    "Eastern Cape": "ec",
    "FS": "fs",
    "Free State": "fs",
    "GP": "gt",
    "Gauteng": "gt",
    "KZN": "nl",
    "KwaZulu-Natal": "nl",
    "LP": "lp",
    "Limpopo": "lp",
    "MP": "mp",
    "Mpumalanga": "mp",
    "NW": "nw",
    "North West": "nw",
    "NC": "nc",
    "Northern Cape": "nc",
    "WC": "wc",
    "Western Cape": "wc",
}


def process_university_data(data, processed=None):
    """
    Takes an iterator, `data` that returns dictionaries of data to be processed
    """
    if processed is None:
        processed = defaultdict(lambda: defaultdict(set))
    for row in data:
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        province = PROVINCE_MAPPING[row["province"]]
        university = row.get("university") or row.get("tvet") or row.get("phei")
        campus = row["campus"]
        processed[province][university].add(campus)
    return processed


if __name__ == "__main__":
    processed = None
    for filename in sys.argv[1:]:
        with open(filename) as f:
            processed = process_university_data(csv.DictReader(f), processed)
    with open("university_data.yaml", "w") as f:
        # YAML library requires normal dictionaries
        data = {
            k1: {k2: list(v2) for k2, v2 in v1.items()} for k1, v1 in processed.items()
        }
        YAML().dump(data, f)
