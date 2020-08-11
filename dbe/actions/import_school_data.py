import argparse
import csv

from whoosh import fields
from whoosh.index import create_in

PROVINCE_MAPPING = {
    "MP": "mp",
    "EC": "ec",
    "KZN": "nl",
    "WC": "wc",
    "NW": "nw",
    "NC": "nc",
    "FS": "fs",
    "LP": "lp",
    "GT": "gt",
}


def read_file(filename):
    schools = set()
    with open(filename) as f:
        print(f"Reading {filename}...")
        for row in csv.DictReader(f):
            schools.add(
                (
                    row["NatEMIS"],
                    PROVINCE_MAPPING[row["Province"]],
                    row["Official_Institution_Name"],
                )
            )
    return schools


def overwrite_index(schools):
    schema = fields.Schema(
        emis=fields.ID(stored=True), province=fields.ID, name=fields.TEXT(stored=True),
    )
    ix = create_in("emis_index", schema)
    writer = ix.writer()
    for school in schools:
        writer.add_document(
            emis=school[0], province=school[1], name=school[2],
        )
    writer.commit(optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import school data into search index")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    schools = set()
    for filename in args.files:
        schools.update(read_file(filename))
    print(f"Read {len(schools)} schools")
    print("Writing index...")
    overwrite_index(schools)
