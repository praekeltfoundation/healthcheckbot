This folder contains helpful tools for cleaning data so that we can classify it, to put it into our training data.

To get the raw data, this SQL query can be useful:
```
COPY(SELECT data::json->'parse_data'->>'text' as text from events where type_name='user') TO STDOUT WITH CSV DELIMITER ',';"
```

There's a `clean.py` script, which takes in the text from stdin, and outputs on stdout.
It filters the inputs, removing any numbers, any blank messages, any matches to the training data, and deduplicates

There's a `get_classification.py` script, which can take the output from `clean.py` into stdin, and query a locally running Rasa server (`rasa run --enable-api`), and output on stdout a CSV with the confidence, category, and text, the 100 texts with the lowest confidence, which can then be used to manually check and correct the classifications.

`insert_classifications.py` takes a csv on stdin in the format that `get_classification.py` exports it as, and adds that data to the NLU training data
