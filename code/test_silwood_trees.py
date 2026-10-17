#!/usr/bin/env python3
"""Tests for clean_silwood_trees.py (standard library only).

Run from the project root:
    python3 code/test_silwood_trees.py        # short report
    python3 code/test_silwood_trees.py -v     # show every test name

The expected results below come from data/silwood_trees_metadata.md,
not from running the program.
"""

import csv
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import clean_silwood_trees as cst


# ---------------------------------------------------------------------------
# Facts copied from the metadata (written here independently of the program)
# ---------------------------------------------------------------------------

COLUMNS = [
    "record_id", "location", "genus", "species", "distance_m", "angle_degrees",
]

# The 16 rejection reasons, in the order the metadata requires.
REASON_ORDER = [
    "missing record_id",
    "invalid record_id",
    "duplicate record_id",
    "missing location",
    "invalid location",
    "missing genus",
    "invalid genus",
    "missing species",
    "invalid species",
    "invalid genus/species combination",
    "missing distance_m",
    "invalid distance_m",
    "distance_m out of range",
    "missing angle_degrees",
    "invalid angle_degrees",
    "angle_degrees out of range",
]

LOCATIONS = ["Silwood Bottom", "Nash's Field", "Manor House", "Reactor Wood"]

VALID_PAIRS = {
    ("Quercus", "robur"),
    ("Quercus", "petraea"),
    ("Acer", "pseudoplatanus"),
    ("Betula", "pendula"),
    ("Fagus", "sylvatica"),
    ("Fraxinus", "excelsior"),
}
GENERA = sorted({genus for genus, _ in VALID_PAIRS})
SPECIES = sorted({species for _, species in VALID_PAIRS})

# Header line of each output file.
HEADERS = {
    "silwood_trees_clean.csv": ",".join(COLUMNS),
    "silwood_tree_issues.csv": "source_row,record_id,reasons",
    "oak_species_counts.csv": "species,count",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def make_row(**changes):
    """Return one valid survey row; keyword arguments replace fields."""
    row = {
        "record_id": "ST001",
        "location": "Manor House",
        "genus": "Acer",
        "species": "pseudoplatanus",
        "distance_m": "10",
        "angle_degrees": "45",
    }
    row.update(changes)
    return row


def oak(species):
    """Return a valid oak record of the given species."""
    return make_row(genus="Quercus", species=species)


def reasons_for(row, accepted_ids=()):
    """Return only the list of rejection reasons for one row."""
    _, reasons = cst.validate_record(row, 2, set(accepted_ids))
    return reasons


def sample_rows():
    """Three rows: two good ones (out of order) and one bad one."""
    return [
        make_row(record_id="ST002", genus="Quercus", species="robur"),
        make_row(record_id="ST001"),
        make_row(record_id="ST003", location="Old Orchard"),
    ]


def read_lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def read_all_files(folder):
    """Return {file name: file bytes} for every file in a folder."""
    return {path.name: path.read_bytes() for path in folder.iterdir()}


def write_survey_file(path, rows):
    """Write rows to a small survey CSV file with the correct header."""
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def run_main(results_dir, rows):
    """Run main() with a temporary output folder and ready-made rows."""
    with mock.patch.object(cst, "RESULTS_DIR", results_dir):
        with mock.patch.object(cst, "load_records", return_value=rows):
            cst.main()


# ---------------------------------------------------------------------------
# 1. Valid records and text cleaning
# ---------------------------------------------------------------------------

class TestValidRecords(unittest.TestCase):

    def test_valid_row_is_accepted(self):
        cleaned, reasons = cst.validate_record(make_row(), 2, set())
        self.assertEqual(reasons, [])
        self.assertEqual(list(cleaned), COLUMNS)
        self.assertTrue(all(isinstance(v, str) for v in cleaned.values()))

    def test_text_is_cleaned_and_written_in_standard_form(self):
        row = make_row(record_id=" ST007 ", location=" silwood bottom ",
                       genus=" quercus ", species=" ROBUR ")
        cleaned, reasons = cst.validate_record(row, 2, set())
        self.assertEqual(reasons, [])
        self.assertEqual(cleaned["record_id"], "ST007")
        self.assertEqual(cleaned["location"], "Silwood Bottom")
        self.assertEqual(cleaned["genus"], "Quercus")
        self.assertEqual(cleaned["species"], "robur")

    def test_every_location_in_any_letter_case(self):
        for location in LOCATIONS:
            for text in (location.lower(), location.upper()):
                with self.subTest(text=text):
                    cleaned, reasons = cst.validate_record(
                        make_row(location=text), 2, set())
                    self.assertEqual(reasons, [])
                    self.assertEqual(cleaned["location"], location)

    def test_every_valid_pair_in_any_letter_case(self):
        for genus, species in sorted(VALID_PAIRS):
            variants = [(genus.lower(), species.upper()),
                        (genus.upper(), species.lower())]
            for genus_text, species_text in variants:
                with self.subTest(genus=genus_text, species=species_text):
                    row = make_row(genus=genus_text, species=species_text)
                    cleaned, reasons = cst.validate_record(row, 2, set())
                    self.assertEqual(reasons, [])
                    self.assertEqual(cleaned["genus"], genus)
                    self.assertEqual(cleaned["species"], species)

    def test_numbers_keep_their_value(self):
        row = make_row(distance_m=" 12.5 ", angle_degrees="35")
        cleaned, reasons = cst.validate_record(row, 2, set())
        self.assertEqual(reasons, [])
        self.assertEqual(float(cleaned["distance_m"]), 12.5)
        self.assertEqual(float(cleaned["angle_degrees"]), 35.0)

    def test_input_row_and_accepted_ids_are_not_changed(self):
        row = make_row(location=" manor house ")
        row_before = dict(row)
        ids = {"ST009"}
        cst.validate_record(row, 2, ids)
        self.assertEqual(row, row_before)
        self.assertEqual(ids, {"ST009"})


# ---------------------------------------------------------------------------
# 2. Missing and invalid values
# ---------------------------------------------------------------------------

class TestMissingAndInvalidValues(unittest.TestCase):

    def test_empty_field_is_missing(self):
        for field in COLUMNS:
            for empty in ("", None):  # None = a row that was too short
                with self.subTest(field=field, value=empty):
                    row = make_row(**{field: empty})
                    self.assertEqual(reasons_for(row), [f"missing {field}"])

    def test_text_fields_with_only_spaces_are_missing(self):
        for field in ("record_id", "location", "genus", "species"):
            with self.subTest(field=field):
                row = make_row(**{field: "   "})
                self.assertEqual(reasons_for(row), [f"missing {field}"])

    def test_invalid_record_ids(self):
        bad_ids = ["TREE27", "st001", "ST01", "ST0012", "ST12A",
                   "XST001", "ST 001"]
        for bad in bad_ids:
            with self.subTest(record_id=bad):
                self.assertEqual(reasons_for(make_row(record_id=bad)),
                                 ["invalid record_id"])

    def test_invalid_locations(self):
        # Misspellings and extra inner spaces are NOT corrected.
        for bad in ["Old Orchard", "Silwood Botom", "Silwood  Bottom",
                    "Manor"]:
            with self.subTest(location=bad):
                self.assertEqual(reasons_for(make_row(location=bad)),
                                 ["invalid location"])

    def test_text_in_number_fields_is_invalid(self):
        for field in ("distance_m", "angle_degrees"):
            for bad in ("forty", "12,5", "12m", "abc"):
                with self.subTest(field=field, value=bad):
                    row = make_row(**{field: bad})
                    self.assertEqual(reasons_for(row), [f"invalid {field}"])


# ---------------------------------------------------------------------------
# 3. Number limits, nan and inf
# ---------------------------------------------------------------------------

class TestNumberLimits(unittest.TestCase):

    def check_accepted(self, field, text):
        """The value is accepted and keeps its numeric value."""
        row = make_row(**{field: text})
        cleaned, reasons = cst.validate_record(row, 2, set())
        self.assertEqual(reasons, [])
        self.assertEqual(float(cleaned[field]), float(text))

    def test_distance_limits(self):
        # Allowed: greater than 0 and at most 100.
        for text in ["0.00001", "0.5", "10", "100", "100.0"]:
            with self.subTest(accepted=text):
                self.check_accepted("distance_m", text)
        for text in ["0", "0.0", "-2", "100.0001", "250"]:
            with self.subTest(rejected=text):
                row = make_row(distance_m=text)
                self.assertEqual(reasons_for(row),
                                 ["distance_m out of range"])

    def test_angle_limits(self):
        # Allowed: greater than 0 and less than 90.
        for text in ["0.01", "45", "89.99"]:
            with self.subTest(accepted=text):
                self.check_accepted("angle_degrees", text)
        for text in ["0", "-1", "90", "90.0", "91"]:
            with self.subTest(rejected=text):
                row = make_row(angle_degrees=text)
                self.assertEqual(reasons_for(row),
                                 ["angle_degrees out of range"])

    def test_nan_and_infinity_are_invalid_not_out_of_range(self):
        for field in ("distance_m", "angle_degrees"):
            for text in ("nan", "NaN", "inf", "-inf", "Infinity"):
                with self.subTest(field=field, value=text):
                    row = make_row(**{field: text})
                    self.assertEqual(reasons_for(row), [f"invalid {field}"])


# ---------------------------------------------------------------------------
# 4. Duplicate identifiers
# ---------------------------------------------------------------------------

class TestDuplicateIds(unittest.TestCase):

    def test_id_already_accepted_is_a_duplicate(self):
        cleaned, reasons = cst.validate_record(make_row(), 2, {"ST001"})
        self.assertIsNone(cleaned)
        self.assertEqual(reasons, ["duplicate record_id"])

    def test_duplicate_check_uses_the_cleaned_id(self):
        row = make_row(record_id=" ST001 ")
        self.assertEqual(reasons_for(row, {"ST001"}), ["duplicate record_id"])

    def test_only_the_first_row_with_an_id_is_accepted(self):
        rows = [make_row(location="Manor House"),
                make_row(location="Reactor Wood"),
                make_row()]
        accepted, issues = cst.process_records(rows)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0]["location"], "Manor House")
        found = [(issue["source_row"], issue["reasons"]) for issue in issues]
        self.assertEqual(found, [("3", "duplicate record_id"),
                                 ("4", "duplicate record_id")])

    def test_invalid_row_does_not_reserve_its_id(self):
        rows = [make_row(location="Old Orchard"),
                make_row(location="Reactor Wood")]
        accepted, issues = cst.process_records(rows)
        self.assertEqual([row["record_id"] for row in accepted], ["ST001"])
        self.assertEqual(accepted[0]["location"], "Reactor Wood")
        self.assertEqual(issues, [{"source_row": "2",
                                   "record_id": "ST001",
                                   "reasons": "invalid location"}])


# ---------------------------------------------------------------------------
# 5. The 16 reasons, several errors in one row, and their order
# ---------------------------------------------------------------------------

class TestRejectionReasons(unittest.TestCase):

    def test_each_of_the_16_reasons_can_be_produced(self):
        cases = [
            ("missing record_id", make_row(record_id=""), set()),
            ("invalid record_id", make_row(record_id="TREE27"), set()),
            ("duplicate record_id", make_row(), {"ST001"}),
            ("missing location", make_row(location=""), set()),
            ("invalid location", make_row(location="Old Orchard"), set()),
            ("missing genus", make_row(genus=""), set()),
            ("invalid genus", make_row(genus="Quercuss"), set()),
            ("missing species", make_row(species=""), set()),
            ("invalid species", make_row(species="robbur"), set()),
            ("invalid genus/species combination",
             make_row(genus="Quercus", species="excelsior"), set()),
            ("missing distance_m", make_row(distance_m=""), set()),
            ("invalid distance_m", make_row(distance_m="forty"), set()),
            ("distance_m out of range", make_row(distance_m="0"), set()),
            ("missing angle_degrees", make_row(angle_degrees=""), set()),
            ("invalid angle_degrees", make_row(angle_degrees="steep"), set()),
            ("angle_degrees out of range", make_row(angle_degrees="90"),
             set()),
        ]
        # The cases themselves must cover all 16 reasons, in order.
        self.assertEqual([case[0] for case in cases], REASON_ORDER)
        for reason, row, ids in cases:
            with self.subTest(reason=reason):
                self.assertEqual(reasons_for(row, ids), [reason])

    def test_several_errors_in_one_row_are_all_reported_in_order(self):
        cases = [
            ("duplicate id and bad location",
             make_row(location="Old Orchard"), {"ST001"},
             ["duplicate record_id", "invalid location"]),
            ("many different problems",
             make_row(record_id="TREE1", location="x", genus="Quercus",
                      species="excelsior", distance_m="abc",
                      angle_degrees="95"),
             set(),
             ["invalid record_id", "invalid location",
              "invalid genus/species combination", "invalid distance_m",
              "angle_degrees out of range"]),
            ("survey-style row",
             make_row(location="Unknown Site", genus="", species="",
                      distance_m="not-a-number", angle_degrees=""),
             set(),
             ["invalid location", "missing genus", "missing species",
              "invalid distance_m", "missing angle_degrees"]),
            ("everything missing",
             make_row(**{field: "" for field in COLUMNS}), set(),
             ["missing " + field for field in COLUMNS]),
            ("duplicate, bad pair and missing distance",
             make_row(genus="Quercus", species="excelsior", distance_m=""),
             {"ST001"},
             ["duplicate record_id", "invalid genus/species combination",
              "missing distance_m"]),
        ]
        for label, row, ids, expected in cases:
            with self.subTest(case=label):
                self.assertEqual(reasons_for(row, ids), expected)
                # The expected list itself must follow the metadata order.
                positions = [REASON_ORDER.index(r) for r in expected]
                self.assertEqual(positions, sorted(positions))

    def test_reasons_are_joined_with_semicolon_and_space(self):
        rows = [make_row(), make_row(location="Old Orchard")]
        _, issues = cst.process_records(rows)
        self.assertEqual(issues[0]["reasons"],
                         "duplicate record_id; invalid location")


# ---------------------------------------------------------------------------
# 6. Genus / species pairs
# ---------------------------------------------------------------------------

class TestGenusSpeciesPairs(unittest.TestCase):

    def test_all_30_combinations(self):
        for genus in GENERA:
            for species in SPECIES:
                with self.subTest(genus=genus, species=species):
                    row = make_row(genus=genus, species=species)
                    reasons = reasons_for(row)
                    if (genus, species) in VALID_PAIRS:
                        self.assertEqual(reasons, [])
                    else:
                        self.assertEqual(
                            reasons, ["invalid genus/species combination"])

    def test_no_pair_reason_unless_both_values_are_recognised(self):
        cases = [
            (make_row(genus="Quercuss", species="robur"), ["invalid genus"]),
            (make_row(genus="Quercus", species="robbur"),
             ["invalid species"]),
            (make_row(genus="Quercuss", species="robbur"),
             ["invalid genus", "invalid species"]),
            (make_row(genus="", species="robur"), ["missing genus"]),
            (make_row(genus="Quercus", species=""), ["missing species"]),
        ]
        for row, expected in cases:
            with self.subTest(genus=row["genus"], species=row["species"]):
                self.assertEqual(reasons_for(row), expected)


# ---------------------------------------------------------------------------
# 7. Oak summary
# ---------------------------------------------------------------------------

class TestOakSummary(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(cst.summarise_oaks([]), [])

    def test_no_oaks(self):
        records = [make_row(), make_row(genus="Betula", species="pendula")]
        self.assertEqual(cst.summarise_oaks(records), [])

    def test_counts_are_sorted_by_species(self):
        records = [oak("robur"), oak("petraea"), make_row(), oak("robur")]
        self.assertEqual(cst.summarise_oaks(records),
                         [{"species": "petraea", "count": "1"},
                          {"species": "robur", "count": "2"}])

    def test_only_species_that_occur_are_listed(self):
        self.assertEqual(cst.summarise_oaks([oak("robur")]),
                         [{"species": "robur", "count": "1"}])

    def test_only_accepted_records_are_counted(self):
        rows = [
            make_row(record_id="ST001", genus="quercus", species="ROBUR"),
            make_row(record_id="ST002", genus="Quercuss", species="robur"),
            make_row(record_id="ST003", genus="Quercus", species="petraea",
                     angle_degrees="95"),
            make_row(record_id="ST004", genus="Quercus", species="petraea"),
        ]
        accepted, _ = cst.process_records(rows)
        # ST001 counts (cleaned to Quercus robur); ST002 is a near match and
        # ST003 has a bad angle, so both are rejected and not counted.
        self.assertEqual(cst.summarise_oaks(accepted),
                         [{"species": "petraea", "count": "1"},
                          {"species": "robur", "count": "1"}])


# ---------------------------------------------------------------------------
# 8. Sorting and source_row
# ---------------------------------------------------------------------------

class TestOrderAndRowNumbers(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(cst.process_records([]), ([], []))

    def test_accepted_rows_are_sorted_by_record_id(self):
        rows = [make_row(record_id="ST010"), make_row(record_id="ST002"),
                make_row(record_id="ST005")]
        accepted, _ = cst.process_records(rows)
        self.assertEqual([row["record_id"] for row in accepted],
                         ["ST002", "ST005", "ST010"])

    def test_issues_keep_file_order_and_source_rows(self):
        rows = [make_row(record_id="ST001"),
                make_row(record_id="ST002", location="Old Orchard"),
                make_row(record_id="ST003"),
                make_row(record_id="ST004", genus="Quercuss")]
        accepted, issues = cst.process_records(rows)
        # The header is line 1, so the first data row is line 2.
        self.assertEqual([issue["source_row"] for issue in issues],
                         ["3", "5"])
        self.assertEqual([issue["record_id"] for issue in issues],
                         ["ST002", "ST004"])
        self.assertEqual(len(accepted) + len(issues), len(rows))

    def test_issue_record_id_is_cleaned_or_empty(self):
        rows = [make_row(record_id=" ST009 ", location="Old Orchard"),
                make_row(record_id="")]
        _, issues = cst.process_records(rows)
        self.assertEqual(issues[0]["record_id"], "ST009")
        self.assertEqual(issues[1]["record_id"], "")

    def test_source_row_matches_the_line_number_in_a_csv_file(self):
        rows = [make_row(record_id="ST001"), make_row(record_id="ST002"),
                make_row(record_id="ST003", angle_degrees="95"),
                make_row(record_id="ST004"), make_row(record_id="ST005")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "small_survey.csv"
            write_survey_file(path, rows)
            accepted, issues = cst.process_records(cst.load_records(path))
        # ST003 is on line 4 (header = 1, ST001 = 2, ST002 = 3).
        self.assertEqual(len(accepted), 4)
        self.assertEqual([issue["source_row"] for issue in issues], ["4"])

    def test_wrong_column_names_raise_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wrong_header.csv"
            path.write_text("record_id,location\nST001,Manor House\n",
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                cst.load_records(path)


# ---------------------------------------------------------------------------
# 9. Import side effects, output files and repeated runs
# ---------------------------------------------------------------------------

class TestOutputFiles(unittest.TestCase):

    def test_importing_the_module_has_no_side_effects(self):
        # Copy only the program into an empty fake project (no data/ folder).
        # If importing read a file, print something or create results/,
        # this test would notice.
        program = Path(cst.__file__).resolve()
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            (project / "code").mkdir()
            shutil.copy(program, project / "code")
            result = subprocess.run(
                [sys.executable, "-c", "import clean_silwood_trees"],
                cwd=project / "code", capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertFalse((project / "results").exists())

    def test_main_creates_results_folder_and_the_three_files(self):
        with tempfile.TemporaryDirectory() as folder:
            results = Path(folder) / "results"  # does not exist yet
            run_main(results, sample_rows())

            names = sorted(path.name for path in results.iterdir())
            self.assertEqual(names, sorted(HEADERS))
            for name, header in HEADERS.items():
                with self.subTest(file=name):
                    self.assertEqual(read_lines(results / name)[0], header)

            clean = read_lines(results / "silwood_trees_clean.csv")
            self.assertEqual(len(clean), 3)  # header + 2 accepted rows
            self.assertTrue(clean[1].startswith("ST001,"))
            self.assertTrue(clean[2].startswith("ST002,"))
            self.assertEqual(
                read_lines(results / "silwood_tree_issues.csv"),
                ["source_row,record_id,reasons", "4,ST003,invalid location"])
            self.assertEqual(
                read_lines(results / "oak_species_counts.csv"),
                ["species,count", "robur,1"])

    def test_running_twice_gives_identical_files(self):
        with tempfile.TemporaryDirectory() as folder:
            results = Path(folder) / "results"
            run_main(results, sample_rows())
            first = read_all_files(results)
            run_main(results, sample_rows())
            second = read_all_files(results)
        self.assertEqual(first, second)

    def test_old_result_files_are_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            results = Path(folder) / "results"
            results.mkdir()
            old_file = results / "oak_species_counts.csv"
            old_file.write_text("old junk\n", encoding="utf-8")
            run_main(results, sample_rows())
            self.assertEqual(read_lines(old_file),
                             ["species,count", "robur,1"])


# ---------------------------------------------------------------------------
# Extra check on the real survey (the small tests above are the main tests)
# ---------------------------------------------------------------------------

@unittest.skipUnless(cst.INPUT_PATH.exists(), "raw survey file not found")
class TestRealSurvey(unittest.TestCase):

    def test_expected_results_for_the_raw_survey(self):
        accepted, issues = cst.process_records(cst.load_records())
        self.assertEqual(len(accepted), 24)
        self.assertEqual(len(issues), 12)
        self.assertEqual(issues[0]["source_row"], "26")
        self.assertEqual(issues[0]["reasons"], "missing record_id")
        self.assertEqual(issues[-1]["source_row"], "37")
        self.assertEqual(cst.summarise_oaks(accepted),
                         [{"species": "petraea", "count": "4"},
                          {"species": "robur", "count": "4"}])

    def test_running_on_the_raw_survey_twice_leaves_it_unchanged(self):
        def fingerprint():
            return hashlib.sha256(cst.INPUT_PATH.read_bytes()).hexdigest()

        before = fingerprint()
        with tempfile.TemporaryDirectory() as folder:
            results = Path(folder) / "results"  # temporary, not the real one
            with mock.patch.object(cst, "RESULTS_DIR", results):
                cst.main()
                first = read_all_files(results)
                cst.main()
                second = read_all_files(results)
        self.assertEqual(first, second)
        self.assertEqual(fingerprint(), before)


if __name__ == "__main__":
    unittest.main()