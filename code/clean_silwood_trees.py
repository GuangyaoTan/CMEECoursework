#!/usr/bin/env python3
"""Validate and clean the synthetic Silwood tree survey."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "silwood_trees_raw.csv"
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_FIELDS = [
    "record_id",
    "location",
    "genus",
    "species",
    "distance_m",
    "angle_degrees",
]
ISSUE_FIELDS = ["source_row", "record_id", "reasons"]
OAK_COUNT_FIELDS = ["species", "count"]


def load_records(path: Path = INPUT_PATH) -> list[dict[str, str]]:
    """Read the survey and check its column names."""
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != INPUT_FIELDS:
            raise ValueError(
                f"Expected columns {INPUT_FIELDS}, found {reader.fieldnames}"
            )
        return list(reader)


def validate_record(
    row: dict[str, str],
    source_row: int,
    accepted_ids: set[str],
) -> tuple[dict[str, str] | None, list[str]]:
    """Clean one record, or return the reasons it cannot be used."""
    reasons = []

    record_id = (row.get("record_id") or "").strip()

    if record_id == "":
        reasons.append("missing record_id")
    elif re.fullmatch(r"ST[0-9]{3}", record_id) is None:
        reasons.append("invalid record_id")
    elif record_id in accepted_ids:
        reasons.append("duplicate record_id")

    location = (row.get("location") or "").strip()

    valid_locations = {
        "silwood bottom": "Silwood Bottom",
        "nash's field": "Nash's Field",
        "manor house": "Manor House",
        "reactor wood": "Reactor Wood",
    }

    if location == "":
        reasons.append("missing location")
    elif location.lower() not in valid_locations:
        reasons.append("invalid location")
    else:
        location = valid_locations[location.lower()]
    
    genus = (row.get("genus") or "").strip()

    valid_genera = {
        "quercus": "Quercus",
        "acer": "Acer",
        "betula": "Betula",
        "fagus": "Fagus",
        "fraxinus": "Fraxinus",
    }

    if genus == "":
        reasons.append("missing genus")
    elif genus.lower() not in valid_genera:
        reasons.append("invalid genus")
    else:
        genus = valid_genera[genus.lower()]
    
    species = (row.get("species") or "").strip()

    valid_species = {
        "robur": "robur",
        "petraea": "petraea",
        "pseudoplatanus": "pseudoplatanus",
        "pendula": "pendula",
        "sylvatica": "sylvatica",
        "excelsior": "excelsior",
    }

    if species == "":
        reasons.append("missing species")
    elif species.lower() not in valid_species:
        reasons.append("invalid species")
    else:
        species = valid_species[species.lower()]
    
    valid_combinations = {
        ("Quercus", "robur"),
        ("Quercus", "petraea"),
        ("Acer", "pseudoplatanus"),
        ("Betula", "pendula"),
        ("Fagus", "sylvatica"),
        ("Fraxinus", "excelsior"),
    }

    if genus in valid_genera.values() and species in valid_species.values():
        if (genus, species) not in valid_combinations:
            reasons.append("invalid genus/species combination")
    
    distance = (row.get("distance_m") or "").strip()

    if distance == "":
        reasons.append("missing distance_m")
    else:
        try:
            distance_value = float(distance)
        except ValueError:
            reasons.append("invalid distance_m")
        else:
            if not math.isfinite(distance_value):
                reasons.append("invalid distance_m")
            elif not 0 < distance_value <= 100:
                reasons.append("distance_m out of range")
            else:
                distance = str(distance_value)
    
    angle = (row.get("angle_degrees") or "").strip()

    if angle == "":
        reasons.append("missing angle_degrees")
    else:
        try:
            angle_value = float(angle)
        except ValueError:
            reasons.append("invalid angle_degrees")
        else:
            if not math.isfinite(angle_value):
                reasons.append("invalid angle_degrees")
            elif not 0 < angle_value < 90:
                reasons.append("angle_degrees out of range")
            else:
                angle = str(angle_value)
    if reasons:
        return None, reasons

    cleaned_record = {
        "record_id": record_id,
        "location": location,
        "genus": genus,
        "species": species,
        "distance_m": distance,
        "angle_degrees": angle,
    }

    return cleaned_record, []


def process_records(
    rows: Iterable[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Sort records into accepted rows and issue reports."""
    accepted = []
    issues = []
    accepted_ids = set()

    for source_row, row in enumerate(rows, start=2):
        cleaned, reasons = validate_record(row, source_row, accepted_ids)

        if cleaned is not None:
            accepted.append(cleaned)
            accepted_ids.add(cleaned["record_id"])
        else:
            issues.append({
                "source_row": str(source_row),
                "record_id": (row.get("record_id") or "").strip(),
                "reasons": "; ".join(reasons),
            })

    accepted.sort(key=lambda row: row["record_id"])

    return accepted, issues


def summarise_oaks(clean_records: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """Count accepted oak records by species."""
    counts = {}

    for row in clean_records:
        if row["genus"] == "Quercus":
            species = row["species"]
            counts[species] = counts.get(species, 0) + 1

    summary = []

    for species in sorted(counts):
        summary.append({
            "species": species,
            "count": str(counts[species]),
        })

    return summary


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: Iterable[dict[str, str]],
) -> None:
    """Write rows to a CSV file, replacing an older copy."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Clean the survey and write the three result files."""
    clean_records, issues = process_records(load_records())
    oak_counts = summarise_oaks(clean_records)

    write_csv(
        RESULTS_DIR / "silwood_trees_clean.csv",
        INPUT_FIELDS,
        clean_records,
    )
    write_csv(
        RESULTS_DIR / "silwood_tree_issues.csv",
        ISSUE_FIELDS,
        issues,
    )
    write_csv(
        RESULTS_DIR / "oak_species_counts.csv",
        OAK_COUNT_FIELDS,
        oak_counts,
    )


if __name__ == "__main__":
    main()
