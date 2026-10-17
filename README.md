CMEE Coursework
This repository contains coursework for the Computational Methods in Ecology and Evolution (CMEE) programme. 
It includes Unix exercises, Shell scripts, Python code, and related practical work. 
The code directory contains scripts and exercise answers, while the data directory stores the original input files, including FASTA sequences and temperature datasets. 
The results directory is used for generated outputs, and the sandbox directory is used for temporary testing. 
Generated results and temporary files are excluded from version control. 
Instructions for running and testing the scripts will be added as the coursework is completed. 
AI assistance, where used, will be documented here with the tool, date, purpose, task, and verification method.

## Bootcamp Assignment 2: Cleaning the Silwood tree survey

This Python program will check and clean a small synthetic tree survey.
The rules come from `data/silwood_trees_metadata.md`.

**Input**

- `data/silwood_trees_raw.csv` (the program must not change this file)

**Output** (written to `results/`; old copies are replaced each run)

- `results/silwood_trees_clean.csv`
- `results/silwood_tree_issues.csv`
- `results/oak_species_counts.csv`

### Plan (pseudocode)

```text
INPUT:  data/silwood_trees_raw.csv
OUTPUT: three CSV files in results/

read the CSV file, one row at a time (the header is line 1)
make two empty lists: accepted and issues
make an empty set: accepted_ids

for each row, in file order:
    source_row = its line number in the CSV (the first data row is 2)
    remove spaces at the start and end of the text values
    match location, genus and species to the permitted values,
        ignoring letter case, and write them in the standard form
        given in the metadata
    check every field using the metadata rules
        (do not correct spelling and do not guess missing values)
    collect ALL the reasons why the row is not valid

    if there are no reasons:
        add the cleaned row to accepted
        add its record_id to accepted_ids
    else:
        add source_row, record_id and the reasons to issues
        (do NOT add the record_id to accepted_ids)

sort accepted by record_id
count the accepted rows whose genus is Quercus, for each species
sort the oak counts by species

write accepted   -> silwood_trees_clean.csv
write issues     -> silwood_tree_issues.csv
write the counts -> oak_species_counts.csv
```

I implemented three functions to follow this plan:
`validate_record` will check one row, `process_records` will loop over
all rows, and `summarise_oaks` will count the oak species.

### What each output file contains

| File | Columns | Content |
| --- | --- | --- |
| `silwood_trees_clean.csv` | `record_id, location, genus, species, distance_m, angle_degrees` | Accepted records only, cleaned and sorted by `record_id` |
| `silwood_tree_issues.csv` | `source_row, record_id, reasons` | Rejected rows in file order, with every reason joined by `; ` |
| `oak_species_counts.csv` | `species, count` | Number of accepted *Quercus* records for each oak species, sorted by species |

### How to run

Run these commands from the `CMEECoursework` root folder:

```bash
python3 code/clean_silwood_trees.py   # clean the data and write results/
python3 code/test_silwood_trees.py    # run the tests
```
The program produced 24 accepted records and 12 rejected records.
The oak counts were 4 petraea and 4 robur.

I ran the automated tests on my computer.
All 40 tests passed.

### A useful test

I included this test in `code/test_silwood_trees.py`.
It will use small made-up records, not the real survey.

| Test record | record_id | location | Other fields |
| --- | --- | --- | --- |
| 1 | `ST001` | `Old Orchard` | valid |
| 2 | `ST001` | `Manor House` | valid |

Expected result:

- Test record 1 is rejected with `invalid location`.
- Test record 2 is accepted, so `ST001` appears once in the clean file.
- The issues file lists only test record 1.

This test would find a bug where an ID is remembered *before* the whole
row is checked. Then the good test record 2 would be wrongly rejected as
`duplicate record_id`. The metadata says an invalid row does not reserve
its ID.

### AI use

I used AI tools to help me understand some English assignment instructions, clarify programming concepts and improve the wording of my documentation. I am responsible for reviewing, testing and submitting my own coursework.

### Known limitations

- The program does not correct spelling mistakes (for example `Quercuss`).
  This is the design required by the metadata, not a program error: it says
  not to correct misspellings or replace a value with the nearest permitted
  one. Rows like this are rejected and listed in the issues file.
- The program reads the whole CSV file into memory, which is fine for this
  small file.