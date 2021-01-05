import csv

from whoosh import fields
from whoosh.index import create_in


def read_file(filename):
    centres = set()
    with open(filename) as f:
        print(f"Reading {filename}...")
        for row in csv.DictReader(f):
            centres.add((row["PROVINCE"], row["NAME"]))
    return centres


def overwrite_index(centres):
    schema = fields.Schema(province=fields.ID, name=fields.TEXT(stored=True))
    ix = create_in("marking_centre_index", schema)
    writer = ix.writer()
    for centre in centres:
        writer.add_document(
            province=centre[0], name=centre[1],
        )
    writer.commit(optimize=True)


if __name__ == "__main__":
    centres = set()
    centres.update(read_file("marking_centres.csv"))
    print(f"Read {len(centres)} centres")
    print("Writing index...")
    overwrite_index(centres)
