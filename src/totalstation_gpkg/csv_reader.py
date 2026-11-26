"""Read and convert total station survey CSV files."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = ("id", "x", "y", "z", "codice")
NUMERIC_COLUMNS = ("x", "y", "z")


class CSVFormatError(ValueError):
    """The CSV does not have the required header or well-formed rows."""


@dataclass(frozen=True)
class PointRecord:
    line_number: int
    point_id: str | None
    x: float | None
    y: float | None
    z: float | None
    code: str | None
    missing_fields: tuple[str, ...]
    invalid_numeric_fields: tuple[str, ...]


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_number(value: str | None) -> tuple[float | None, bool]:
    cleaned = _clean_text(value)
    if cleaned is None:
        return None, False
    try:
        number = float(cleaned)
    except ValueError:
        return None, True
    if not math.isfinite(number):
        return None, True
    return number, False


def read_points(csv_path: str | Path) -> list[PointRecord]:
    """Read the CSV and retain numeric errors for the validation report."""
    records: list[PointRecord] = []
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise CSVFormatError("The CSV is empty or has no header.")
        if len(fieldnames) != len(set(fieldnames)):
            raise CSVFormatError("The header contains duplicate column names.")

        normalized_names = {name.strip(): name for name in fieldnames}
        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in normalized_names
        ]
        if missing_columns:
            raise CSVFormatError(
                "Missing required columns in header: " + ", ".join(missing_columns)
            )

        for row in reader:
            line_number = reader.line_num
            if None in row:
                raise CSVFormatError(
                    f"CSV row {line_number} contains more fields than the header."
                )

            values = {
                column: row.get(normalized_names[column])
                for column in REQUIRED_COLUMNS
            }
            missing_fields = tuple(
                column
                for column in REQUIRED_COLUMNS
                if _clean_text(values[column]) is None
            )
            parsed_numbers: dict[str, float | None] = {}
            invalid_numeric_fields: list[str] = []
            for column in NUMERIC_COLUMNS:
                number, invalid = _parse_number(values[column])
                parsed_numbers[column] = number
                if invalid:
                    invalid_numeric_fields.append(column)

            records.append(
                PointRecord(
                    line_number=line_number,
                    point_id=_clean_text(values["id"]),
                    x=parsed_numbers["x"],
                    y=parsed_numbers["y"],
                    z=parsed_numbers["z"],
                    code=_clean_text(values["codice"]),
                    missing_fields=missing_fields,
                    invalid_numeric_fields=tuple(invalid_numeric_fields),
                )
            )
    return records
