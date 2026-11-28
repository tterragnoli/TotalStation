from totalstation_gpkg.csv_reader import PointRecord
from totalstation_gpkg.validation import validate_points


def _record(line_number, point_id, z, code="MANHOLE"):
    return PointRecord(
        line_number=line_number,
        point_id=point_id,
        x=float(line_number),
        y=float(line_number),
        z=z,
        code=code,
        missing_fields=(),
        invalid_numeric_fields=(),
    )


def test_validation_finds_duplicate_ids_and_per_code_height_outlier():
    records = [
        _record(2, "A", 10.0),
        _record(3, "B", 10.1),
        _record(4, "C", 9.9),
        _record(5, "D", 10.0),
        _record(6, "A", 100.0),
        _record(7, "E", 50.0, code="TREE"),
    ]

    report = validate_points(records)

    assert report.duplicate_ids[0].point_id == "A"
    assert report.duplicate_ids[0].line_numbers == (2, 6)
    assert [(item.point_id, item.code) for item in report.anomalous_heights] == [
        ("A", "MANHOLE")
    ]


def test_validation_skips_codes_with_fewer_than_five_valid_heights():
    report = validate_points(
        [_record(2, "A", 1.0), _record(3, "B", 100.0), _record(4, "C", 1.0)]
    )

    assert report.anomalous_heights == ()


def test_validation_flags_values_different_from_median_when_mad_is_zero():
    records = [
        _record(2, "A", 10.0),
        _record(3, "B", 10.0),
        _record(4, "C", 10.0),
        _record(5, "D", 10.0),
        _record(6, "E", 12.0),
    ]

    report = validate_points(records)

    assert len(report.anomalous_heights) == 1
    assert report.anomalous_heights[0].point_id == "E"
    assert report.anomalous_heights[0].modified_z_score is None


def test_validation_tolerance_ignores_close_elevations_with_nonzero_mad():
    records = [
        _record(2, "A", 10.0),
        _record(3, "B", 10.0),
        _record(4, "C", 10.0),
        _record(5, "D", 10.02),
        _record(6, "E", 12.0),
    ]

    report = validate_points(records)

    assert [item.point_id for item in report.anomalous_heights] == ["E"]


def test_validation_tolerance_ignores_close_elevations_when_mad_is_zero():
    records = [
        _record(2, "A", 10.0),
        _record(3, "B", 10.0),
        _record(4, "C", 10.0),
        _record(5, "D", 10.0),
        _record(6, "E", 10.02),
    ]

    report = validate_points(records)

    assert report.anomalous_heights == ()
