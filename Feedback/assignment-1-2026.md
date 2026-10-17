# Assignment 1 feedback - Guangyao Tan

**Formative feedback | Rubric 2026.2**

The FASTA work is clearly explained, and all five answers matched the independent checks, including the ratio at its reported precision. Your discussion of ambiguity symbols and motifs crossing line breaks is particularly useful. The README also records dependencies and how you used and checked assistance.

The main correction is in the converters, not the sequence calculations. Both write through ../results, which assumes they are launched from code/. The assignment requires the converters to work from the repository root. Change the scripts and examples together, then try them in a fresh checkout with no results directory already present. Several output checks share this path problem; they are not separate algorithmic mistakes.

Bring tabtocsv.sh's checking up to the standard already present in csvtospace.sh. It needs to accept exactly one readable regular file, create its output directory and stop with an error if conversion fails. A Done message should tell you that the output was actually produced, not just that execution reached the end of the script.

Add your own data/tab-example.tsv and include a deliberately empty field. Record what you expected and what appeared in the output, along with a spaced filename and a repeated run. Keep the results ignore rules; the tracked .gitkeep is only a directory placeholder. More specific commit messages will make the next round of changes easier to follow.

---

## Project structure

Relevant tracked layout (simplified; missing required paths are marked):

```text
README.md
.gitignore
code/  unixPrac1.txt, tabtocsv.sh, csvtospace.sh
data/fasta/  3 required files present
data/temperatures/  4 required files present
data/tab-example.tsv [missing]
results/  placeholder only
sandbox/  placeholder only
```

The root README, ignore file, assessed code and supplied input directories are in place. The only required path missing is data/tab-example.tsv. results/ and sandbox/ contain placeholders rather than generated files, and their ignore rules already protect the intended separation.

Add a useful own TSV and retain this layout. There is no need for another results directory outside the repository: correct the converter paths so they use this project's results/. The .gitkeep files are harmless placeholders and do not need to be removed.

**Assessed snapshot:** `b9fe5276ec6d50ac402207bf1f65acf1a4e44043`
