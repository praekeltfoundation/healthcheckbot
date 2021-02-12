Importing University/TVET/PHEI data
-----------------------------------
The source for this information was given directly by Higher Health

Current info is from 2 November 2020.

That data is in Excel xlsx format, so use something like `ssconvert` to convert it to CSV:
```bash
~ ssconvert -S tvet_university_phei.xlxs data.csv
```

Then to import, use the `import_university_data.py` script, which accepts a list of CSV files as arguments, processes them, and outputs to the `university_data.yaml` file. It always appends to the current list of data in the yaml file. To overwrite, first clear the yaml file.

```bash
~ python import_university_data.py data.csv.0 data.csv.1 data.csv.2
```

Then update this readme and commit the `university_data.yaml` file, to update the list of universities and campuses
