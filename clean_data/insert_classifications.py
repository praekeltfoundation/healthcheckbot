import csv
import sys

for (_, intent, text) in csv.reader(sys.stdin):
    with open(f"../base/data/nlu/{intent}.md", "a") as f:
        f.write(f"- {text}\n")
