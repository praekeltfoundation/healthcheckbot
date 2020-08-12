Importing school/EMIS data
--------------------------
The source for the EMIS information was downloaded from https://www.education.gov.za/Programmes/EMIS/EMISDownloads.aspx

Current info is from "Quarter 4 of 2019: March 2020", except for Northern Cape, which is from "Quarter 3 of 2019: December 2019", as there's an error trying to download that file.

That data is in Excel xlsx format, so use something like `ssconvert` to convert it to CSV:
```bash
~ for f in *.xlsx; do ssconvert "$f" "${f%.xlsx}.csv"; done
```

For the current data, the "Special Needs Education Centres.xlsx" file had different headings to the rest, so the headings were manually edited. The important headings are `NatEMIS`, `Province`, and `Official_Institution_Name`.

Then to import, use the `import_school_data.py` script, which accepts a list of CSV files as arguments, processes them and deduplicates entries, builds the search index, and outputs the index to the `emis_index` folder. This script will always overwrite all the data in `emis_index`.

```bash
~ python import_school_data.py Eastern\ Cape.csv Free\ State.csv Gauteng.csv KwaZulu\ Natal.csv Limpopo.csv Mpumalanga.csv National.csv North\ West.csv Northern\ Cape.csv Special\ Needs\ Education\ Centres.csv Western\ Cape.csv
```

Then commit the files in the `emis_index` folder, to update the search index.
