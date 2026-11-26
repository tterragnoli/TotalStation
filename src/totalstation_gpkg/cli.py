"""Command-line interface for processing total station survey data."""

import argparse
from pathlib import Path
from typing import Sequence

from pyproj import CRS
from pyproj.exceptions import CRSError

from totalstation_gpkg.csv_reader import CSVFormatError, read_points
from totalstation_gpkg.geopackage import export_geopackage
from totalstation_gpkg.validation import ValidationReport, validate_points


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a total station CSV and export a GeoPackage."
    )
    parser.add_argument("input_csv", type=Path, help="Input points CSV file")
    parser.add_argument("output_gpkg", type=Path, help="GeoPackage output file")
    parser.add_argument(
        "--crs",
        required=True,
        help="Coordinate reference system, for example EPSG:32632",
    )
    return parser


def _print_report(report: ValidationReport) -> None:
    print("Validation report:")
    if report.duplicate_ids:
        for duplicate in report.duplicate_ids:
            lines = ", ".join(str(line) for line in duplicate.line_numbers)
            print(f"  Duplicate ID {duplicate.point_id!r}: rows {lines}")
    else:
        print("  No duplicate IDs.")

    for missing in report.missing_values:
        print(f"  Missing value: row {missing.line_number}, field {missing.field}")
    if not report.missing_values:
        print("  No missing values.")

    for invalid in report.invalid_numbers:
        print(
            f"  Invalid number: row {invalid.line_number}, field {invalid.field}"
        )
    if not report.invalid_numbers:
        print("  No invalid numeric values.")

    for anomaly in report.anomalous_heights:
        score = (
            "MAD is zero"
            if anomaly.modified_z_score is None
            else f"z-MAD={anomaly.modified_z_score:.2f}"
        )
        print(
            f"  Anomalous elevation: row {anomaly.line_number}, "
            f"ID {anomaly.point_id!r}, code {anomaly.code!r}, "
            f"Z={anomaly.z:g} ({score})"
        )
    if not report.anomalous_heights:
        print("  No anomalous elevations.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        CRS.from_user_input(args.crs)
        records = read_points(args.input_csv)
        report = validate_points(records)
        _print_report(report)
        exported = export_geopackage(records, args.output_gpkg, args.crs)
    except (CSVFormatError, CRSError, OSError, ValueError) as error:
        parser.error(str(error))

    excluded = len(records) - exported
    print(f"Exported {exported} points to {args.output_gpkg}.")
    if excluded:
        print(f"Excluded {excluded} records without valid X and Y coordinates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
