# CMEE Coursework

This repository contains my coursework for Computational Methods in Ecology and Evolution (CMEE).

# Bootcamp Assignment 1

This assignment includes five Unix FASTA exercises and two Shell scripts: `tabtocsv.sh` and `csvtospace.sh`.

## Running and Testing

Run the scripts from the `code/` folder:

```bash
bash tabtocsv.sh ../sandbox/test.tsv
bash csvtospace.sh ../data/temperatures/1800.csv
```

I tested the scripts using sample data and checked their outputs and error messages. Generated results are not committed to GitHub.

## Dependencies

The scripts use Bash and standard Unix tools such as tr, awk, grep, wc, and basename.

## AI Use

I used ChatGPT (OpenAI) on 8 October 2026. For `unixPrac1.txt`, I mainly used AI to help translate between Chinese and English and improve my explanations. For the Shell scripting and Git tasks, I used AI to understand the workflow, ask questions and troubleshoot errors. I checked the suggestions by running the commands and testing the scripts in VS Code.


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

  ## Bootcamp Assignment 3

### Part 1: Tree Heights

This task calculates tree heights using distance and angle measurements from `data/trees.csv`.

Run from the repository root:

`Rscript code/TreeHeight.R`

`Rscript code/get_TreeHeight.R data/trees.csv`

`bash code/run_get_TreeHeight.sh`

The scripts generate `results/TreeHts.csv` and `results/trees_treeheights.csv`. Both outputs contain 120 records and four columns. I checked the first tree's height (27.80 m) and tested the command-line error handling.

### Part 2: Pound Hill Species Richness

This task compares plant species richness among March, May and October cultivation treatments.

Run from the repository root:

`Rscript code/pound_hill_analysis.R`

The script reads `data/pound_hill_data.csv` and `data/pound_hill_meta_data.csv`, without modifying them. Blank species counts are treated as zeros according to the metadata.

Richness is calculated for each quadrat, then averaged within each plot. The analysis includes 41 species, 59 quadrats and 12 plots.

The script generates `results/pound_hill_plot_richness.csv` and `results/pound_hill_plot_richness.pdf`. I checked that the CSV contains 12 plots and the figure shows four plot values per treatment.

May had the highest average richness (9.65 species per quadrat), followed by March (7.81) and October (7.61). The values overlap across treatments, so the figure does not prove that cultivation timing caused these differences.

Generated results are excluded from GitHub because they can be reproduced by running the scripts.