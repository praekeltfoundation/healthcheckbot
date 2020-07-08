import csv
import sys

import requests

results = []

for (text,) in csv.reader(sys.stdin):
    r = requests.post("http://localhost:5005/model/parse", json={"text": text})
    r.raise_for_status()
    data = r.json()
    results.append((data["intent"]["confidence"], data["intent"]["name"], text))

results.sort()

output = csv.writer(sys.stdout)

for item in results[:100]:
    output.writerow(item)
