import geopandas as gpd

from totalstation_gpkg.csv_reader import PointRecord
from totalstation_gpkg.geopackage import export_geopackage


def test_export_geopackage_uses_crs_and_skips_missing_xy(tmp_path):
    records = [
        PointRecord(2, "P1", 10.0, 20.0, 3.0, "MANHOLE", (), ()),
        PointRecord(3, "P2", None, 21.0, 4.0, "MANHOLE", ("x",), ()),
    ]
    output_path = tmp_path / "points.gpkg"

    exported_count = export_geopackage(records, output_path, "EPSG:32632")
    result = gpd.read_file(output_path, layer="points")

    assert exported_count == 1
    assert len(result) == 1
    assert result.iloc[0]["id"] == "P1"
    assert result.crs.to_epsg() == 32632
    assert result.geometry.iloc[0].x == 10.0
    assert result.geometry.iloc[0].y == 20.0
