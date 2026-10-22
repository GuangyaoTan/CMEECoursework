# Assignment 2 formative feedback

This feedback is organised by the relevant computing bootcamp criteria. Use it to decide what is already working, what you need to investigate, and what to revise before the cumulative submission.

The full criteria are in the [Computing Bootcamp assessment rubric](https://github.com/MulQuaBio/MQB/blob/main/content/rubrics/Computing_Bootcamp_Rubric.md).

## 1. Repository organisation and workflow discipline

- Your root README, `.gitignore`, cleaning script, test script and supplied data files are in the expected locations. The supplied CSV and metadata are unchanged, giving you a reproducible starting point.

## 2. Code completeness and functional correctness

- The cleaning script executed successfully. Separately, output checks found that all three output tables satisfied the requirements on both test runs. The outputs are correct for the checked input; before final submission, test a few important edge cases and make sure you can explain the method.

## 3. Code quality and style

- Your `main()` function gives the program a clear overall structure by connecting loading, processing, summarising and writing. Keep these stages distinct as you revise; use descriptive names and add short comments where the reason for a validation check or data-cleaning step is not obvious.

## 4. Documentation

- Your root README is in place. Make it useful to someone opening the repository for the first time: explain what the cleaner does, how to run the script and tests from the repository root, and which three files it creates. Test the instructions in a newly cloned copy of your repository (a separate folder created with `git clone`): enter that folder and run each README command exactly as written. If something fails, correct the command or add the missing step.

## 5. Version-control practice

- Since the previous formative feedback was added, the saved history contains 1 non-merge commit. Assignment 2 appears in one recent commit, `Complete Bootcamp Assignment 2 tree survey cleaning`. This records a finished snapshot, but not the stages used to reach it.
- For the final revisions, avoid another single catch-all commit. Commit one working change at a time—for example, a code correction, its test, then the README update. Check each staged change with `git diff --staged` before writing the message.

## 8. Basic error handling and input validation

- Your separate test file ran successfully. Your test file includes tests for record validation, accepted/rejected partitioning, oak summaries and end-to-end writing and execution—useful coverage across the workflow.
- **Check what the tests demonstrate, not just their exit status.** The test script ran without errors, but its output content was not checked. Review a representative validation, partition and summary test to ensure each asserts the intended behaviour. If you find a gap, add a small focused case rather than duplicating existing coverage.
- Add the valid/invalid-record assertions to your separate test file, then rerun the tests and cleaning workflow from the documented working directory.
- Check that the root README explains purpose, run commands, test commands and the three outputs. Test the instructions in a newly cloned copy of your repository (a separate folder created with `git clone`): enter that folder and run each README command exactly as written. If something fails, correct the command or add the missing step.

## 9. Problem-solving approach and method implementation

- Your code shows a connected workflow: `main()` loads rows through `load_records()`, passes them to `process_records()` and `validate_record()`, receives `(accepted, issues)`, summarises the cleaned collection with `summarise_oaks()`, and writes three outputs. The flow from input to outputs is easy to follow.
- Before final submission, make this check visible in your repository. In `code/test_silwood_trees.py`, add or refine a small assertion-based test with one valid and one invalid record. Check that `process_records()` places them in the cleaned and issues collections respectively. Then pass the returned cleaned collection to `summarise_oaks()` and check that the invalid record does not contribute. Briefly explain this flow in your root README.
