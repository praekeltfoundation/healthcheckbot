import csv
import sys
from collections import defaultdict
from typing import Dict, Iterable, Optional, Set, Text

from ruamel.yaml import round_trip_dump, round_trip_load
from ruamel.yaml.comments import CommentedMap

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


def process_university_data(
    data: Iterable[Dict[Text, Text]],
    processed: Optional[Dict[Text, Dict[Text, Set[Text]]]] = None,
) -> Dict[Text, Dict[Text, Set[Text]]]:
    """
    Takes an iterator, `data` that returns dictionaries of data to be processed
    """
    if processed is None:
        processed = defaultdict(lambda: defaultdict(set))
    for row in data:
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        province = PROVINCE_MAPPING[row["province"]]
        university = row.get("university") or row.get("tvet") or row["phei"]
        campus = row["campus"]
        processed[province][instutution] = set(campuses)
    return processed


def sort_data(data: Dict[Text, Dict[Text, Set[Text]]]) -> CommentedMap:
    """
    Takes the university data, and returns an alphabetically sorted version of the data,
    sorting the province, university, and campuses
    """
    result = CommentedMap()
    for province in sorted(data.keys()):
        result[province] = CommentedMap()
        for university in sorted(data[province].keys()):
            result[province][university] = sorted(data[province][university])
    return result


if __name__ == "__main__":
    processed: Dict[Text, Dict[Text, Set[Text]]] = defaultdict(lambda: defaultdict(set))

    with open("university_data.yaml") as f:
        data = round_trip_load(f)
        for province, inst_data in data.items():
            for instutution, campuses in inst_data.items():
                processed[province][instutution] = campuses

    for filename in sys.argv[1:]:
        with open(filename) as f:
            processed = process_university_data(csv.DictReader(f), processed)

    with open("university_data.yaml", "w") as f:
        round_trip_dump(sort_data(processed), f)
