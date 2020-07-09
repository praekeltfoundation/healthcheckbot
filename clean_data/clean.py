import asyncio
import csv
import sys

from rasa.importers.importer import TrainingDataImporter


def is_number(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def get_training_data():
    importer = TrainingDataImporter.load_from_config(
        "../config.yml", "../base/domain-eng.yml", ["../base/data/"]
    )
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(importer.get_nlu_data())
    return set(i.text.lower().strip() for i in data.intent_examples)


training_data = get_training_data()
existing = set()
output = csv.writer(sys.stdout)

for (text,) in csv.reader(sys.stdin):
    if is_number(text):
        continue
    if not text:
        continue
    if text.lower().strip() in training_data:
        continue
    if text.lower().strip() in existing:
        continue

    output.writerow([text])
    existing.add(text.lower().strip())
