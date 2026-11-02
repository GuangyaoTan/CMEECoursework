# CMEE Coursework

This repository contains my coursework for Computational Methods in Ecology and Evolution (CMEE).

# Bootcamp Assignment 1

This assignment includes five Unix FASTA exercises and two Shell scripts: `tabtocsv.sh` and `csvtospace.sh`.

## Running and Testing

Run from the repository root:

```bash
bash code/tabtocsv.sh data/tab-example.tsv
bash code/csvtospace.sh data/temperatures/1800.csv
```

Outputs are `results/tab-example.tsv.csv` and `results/1800.csv.txt`.
Both scripts locate `results/` relative to their own location and create it
when needed. Each accepts exactly one readable regular file and replaces its
output on repeated runs. `Done!` is printed only after successful conversion;
invalid input, directory creation failure or conversion failure exits nonzero.
These scripts replace delimiter characters literally; they do not parse quoted CSV.

### Test evidence (30 October 2026)

I ran both commands above from the repository root and compared the complete
output bytes with the expected delimiter substitutions. Both passed.
`data/tab-example.tsv` deliberately has an empty site field in the oak row.
Expected CSV: `oak,,3`. Actual CSV: `oak,,3`; the empty field was preserved.
The equivalent comma-to-space test produced `oak  3` (two spaces).

I also tested copies of the current scripts in an isolated temporary repository
layout so that existing results were preserved:

| Check (both scripts) | Expected and observed result |
| --- | --- |
| No results directory / empty results directory | Directory created when absent; correct output produced |
| Input filename containing spaces | Correctly named output with exact expected contents |
| Run twice with the same input | Output replaced; identical contents, no duplicated rows |
| Zero or two arguments | Nonzero exit, error message, no Done |
| Missing file, directory input, unreadable file | Nonzero exit, error message, no Done |
| A regular file blocking results directory creation | Nonzero exit, error message, no Done |
| A directory blocking the output file | Nonzero exit, error message, no Done |
| A test replacement for tr returning failure | Nonzero exit, error message, no Done |
| Bash syntax check (`bash -n`) | Both scripts passed |

Generated results remain ignored; `results/.gitkeep` and `sandbox/.gitkeep`
remain directory placeholders.

## Dependencies

The converters use Bash, tr, dirname, basename and mkdir. The Unix FASTA
exercises also use standard Unix tools including awk, grep and wc.

## AI Use

I used ChatGPT (OpenAI) on 8 October 2026. For `unixPrac1.txt`, I mainly used AI to help translate between Chinese and English and improve my explanations. For the Shell scripting and Git tasks, I used AI to understand the workflow, ask questions and troubleshoot errors. I checked the suggestions by running the commands and testing the scripts in VS Code.

On 30 October 2026, I used Codex to apply the Assignment 1 formative feedback:
update the converter paths and error handling, add the empty-field example,
run the checks reported above and update this documentation.


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
All 41 tests passed.

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

**Independent tree-height validation:** For the first tree in `data/trees.csv`, the measured angle was 41.28264° and the horizontal distance was 31.66583 m. Independently applying `distance × tan(angle × π / 180)` gave a height of 27.80212 m. This agreed with the first `height_m` value in `results/TreeHts.csv`. The comparison passed using `all.equal()` without calling the `TreeHeight()` function.

### Assignment 3: Revisions and validation

**Tree-height function:** Following formative feedback, I added the reusable `TreeHeight(angle_degrees, distance_m)` function to `code/TreeHeight.R`. The function converts degrees to radians and calculates height using `distance_m * tan(angle_degrees * pi / 180)`. I checked that `TreeHeight(45, 10)` returns 10 m.

**Independent height check:** For the first tree in `data/trees.csv`, the angle was 41.28264° and the horizontal distance was 31.66583 m. Applying the trigonometric formula independently gave 27.80212 m, matching the first height in `results/TreeHts.csv`.

**Normal and invalid input tests:** Both `Rscript code/TreeHeight.R` and `bash code/run_get_TreeHeight.sh` completed successfully and generated CSVs containing 120 rows. I also tested an invalid distance of 0 m using temporary copies of the input data. Both programs exited with status 1 and reported a distance validation error. Neither produced a new output file for the invalid input.

**Pound Hill validation:** Running `Rscript code/pound_hill_analysis.R` regenerated the plot richness CSV and PDF. For the October treatment, Block a, Plot 1, the five quadrat species richness values independently calculated from the supplied data were 7, 8, 7, 5 and 8. Their mean was 7.0, matching the plot-level value in `results/pound_hill_plot_richness.csv`.

Generated results are stored under `results/` and are not intended to be committed to Git.

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

### AI use
I used AI to help understand the assignment instructions, develop and review R code. I ran the scripts on my own computer, checked the results and figure, and reviewed the final work before submission.

## Assignment 4: Practice Scripts and Final Checks

This portfolio includes 30 classroom practice scripts: 7 Shell, 12 Python and 11 R scripts. Run all commands from the repository root. Code is stored in code/, input data in data/, and generated files in results/.

### Shell (7 scripts)

Run variables.sh, MyExampleScript.sh and boilerplate.sh using bash code/<filename>.

Run CheckLabel.sh with valid and invalid labels; CountLines.sh with existing and missing files; and ConcatenateTwoFiles.sh with two inputs and an output file. Check the contents, errors and exit codes.

Check tiff2_png.sh using bash -n code/tiff2_png.sh. Actual conversion was not tested because ImageMagick was unavailable.

### Python (12 scripts)

Run each script using python3 code/<filename>:

loops.py, cfexercises1.py, cfexercises2.py, MyExampleScript.py, boilerplate.py, using_name.py, sysargv.py, control_flow.py, test_control_flow.py, observations_practice.py, test_observations_practice.py, debugme.py.

For sysargv.py, provide a sample argument such as test. The observation exercises use the three data/bootcamp_observations*.csv files and check ordinary, boundary and invalid cases.

### R (11 scripts)

Run each script using Rscript code/<filename>:

basic_io.R, boilerplate.R, control_flow.R, r_conditionals.R, break.R, next.R, try.R, browse.R, observations_practice.R, data_wrang.R, data_wrang_tidy.R.

For interactive debugging, start R using R --vanilla, then run source("code/browse.R"). Use Q to exit the debugger.

The observation script checks missing and zero counts and generates a PDF. The data-wrangling scripts use the Pound Hill datasets.

### Dependencies

Requires Bash, Python 3 and R. R data-wrangling requires reshape2, dplyr and tidyr. TIFF conversion additionally requires ImageMagick.

### Verification

All 11 R scripts passed syntax checks and basic execution tests. The Python observation checks passed, and Assignment 2 passed all 41 tests.

Following formative feedback, I improved the Assignment 1 converters and added TSV test data. I also added the reusable TreeHeight() function. Both tree-height programs successfully generated 120 records and rejected invalid distances.

An independent tree-height calculation gave 27.80212 m, matching the CSV. The Pound Hill quadrat richness values 7, 8, 7, 5 and 8 gave a mean of 7.0, also matching the CSV.

Generated results are excluded from Git. On 2 November 2026, I cloned the GitHub repository into a separate directory and ran the portfolio checks from the repository root. The Assignment 1–3 programs ran successfully, all 41 Silwood tests passed, and all 12 Python and 11 R practice scripts completed successfully. The Shell scripts passed syntax checks, with functional checks for the main examples. Generated results were ignored by Git, and the source data remained unchanged. Actual TIFF conversion was not tested because ImageMagick was unavailable.

### AI Use

I used AI to understand instructions, revise parts of the code, and improve documentation. I reviewed and tested the work locally and remain responsible for the final submission.