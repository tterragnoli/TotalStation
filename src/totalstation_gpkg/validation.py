"""Validate survey points and identify anomalous elevations per code."""

from collections import defaultdict
from dataclasses import dataclass
from statistics import median

from totalstation_gpkg.csv_reader import PointRecord
from totalstation_gpkg.config import MAD_THRESHOLD, MIN_GROUP_SIZE

MAD_NORMALIZATION = 0.6744897501960817


@dataclass(frozen=True)
class DuplicateID:
    point_id: str
    line_numbers: tuple[int, ...]


@dataclass(frozen=True)
class MissingValue:
    line_number: int
    field: str


@dataclass(frozen=True)
class InvalidNumber:
    line_number: int
    field: str


@dataclass(frozen=True)
class AnomalousHeight:
    line_number: int
    point_id: str | None
    code: str
    z: float
    modified_z_score: float | None


@dataclass(frozen=True)
class ValidationReport:
    duplicate_ids: tuple[DuplicateID, ...]
    missing_values: tuple[MissingValue, ...]
    invalid_numbers: tuple[InvalidNumber, ...]
    anomalous_heights: tuple[AnomalousHeight, ...]


def validate_points(records: list[PointRecord]) -> ValidationReport:
    """Find duplicate IDs, missing values, invalid numbers, and height outliers."""
    id_lines: dict[str, list[int]] = defaultdict(list)
    missing_values: list[MissingValue] = []
    invalid_numbers: list[InvalidNumber] = []
    heights_by_code: dict[str, list[PointRecord]] = defaultdict(list)

    for record in records:
        if record.point_id is not None:
            id_lines[record.point_id].append(record.line_number)
        missing_values.extend(
            MissingValue(record.line_number, field)
            for field in record.missing_fields
        )
        invalid_numbers.extend(
            InvalidNumber(record.line_number, field)
            for field in record.invalid_numeric_fields
        )
        if record.code is not None and record.z is not None:
            heights_by_code[record.code].append(record)

    duplicate_ids = tuple(
        DuplicateID(point_id, tuple(line_numbers))
        for point_id, line_numbers in sorted(id_lines.items())
        if len(line_numbers) > 1
    )
    anomalous_heights: list[AnomalousHeight] = []
    for code, group in sorted(heights_by_code.items()):
        if len(group) < MIN_GROUP_SIZE:
            continue
        heights = [record.z for record in group]
        group_median = median(heights)
        mad = median([abs(height - group_median) for height in heights])
        for record in group:
            if mad == 0:
                if record.z == group_median:
                    continue
                score = None
            else:
                score = (
                    MAD_NORMALIZATION * (record.z - group_median) / mad
                )
                if abs(score) <= MAD_THRESHOLD:
                    continue
            anomalous_heights.append(
                AnomalousHeight(
                    line_number=record.line_number,
                    point_id=record.point_id,
                    code=code,
                    z=record.z,
                    modified_z_score=score,
                )
            )

    return ValidationReport(
        duplicate_ids=duplicate_ids,
        missing_values=tuple(missing_values),
        invalid_numbers=tuple(invalid_numbers),
        anomalous_heights=tuple(anomalous_heights),
    )
