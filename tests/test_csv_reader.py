import pytest

from totalstation_gpkg.csv_reader import CSVFormatError, read_points


def test_read_points_tracks_missing_and_invalid_values(tmp_path):
    csv_path = tmp_path / "points.csv"
    csv_path.write_text(
        "id,x,y,z,codice\n"
        "P1,1.5,2,3,CAP\n"
        "P2,,abc,NaN,\n",
        encoding="utf-8",
    )

    records = read_points(csv_path)

    assert records[0].x == 1.5
    assert records[1].missing_fields == ("x", "codice")
    assert records[1].invalid_numeric_fields == ("y", "z")
    assert records[1].y is None
    assert records[1].z is None


def test_read_points_requires_all_columns(tmp_path):
    csv_path = tmp_path / "points.csv"
    csv_path.write_text("id,x,y,z\nP1,1,2,3\n", encoding="utf-8")

    with pytest.raises(CSVFormatError, match="codice"):
        read_points(csv_path)


def test_read_points_explains_semicolon_delimiters(tmp_path):
    csv_path = tmp_path / "points.csv"
    csv_path.write_text("id;x;y;z;codice\nP1;1,5;2,0;3,0;CAP\n", encoding="utf-8")

    with pytest.raises(CSVFormatError, match="commas as delimiters"):
        read_points(csv_path)


def test_read_points_explains_csv_utf8_encoding(tmp_path):
    csv_path = tmp_path / "points.csv"
    csv_path.write_bytes(b"id,x,y,z,codice\nP1,\xff,2,3,CAP\n")

    with pytest.raises(CSVFormatError, match="CSV UTF-8"):
        read_points(csv_path)
