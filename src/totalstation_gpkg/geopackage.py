"""Export points with valid planimetric coordinates to a GeoPackage."""

from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Point

from totalstation_gpkg.csv_reader import PointRecord
from totalstation_gpkg.config import LAYER_NAME


def export_geopackage(
    records: list[PointRecord],
    output_path: str | Path,
    crs: str,
) -> int:
    """Export records with valid X/Y coordinates and return the feature count."""
    parsed_crs = CRS.from_user_input(crs)
    point_records = [record for record in records if record.x is not None and record.y is not None]
    frame = gpd.GeoDataFrame(
        {
            "id": [record.point_id for record in point_records],
            "x": [record.x for record in point_records],
            "y": [record.y for record in point_records],
            "z": [record.z for record in point_records],
            "codice": [record.code for record in point_records],
        },
        geometry=[
            Point(record.x, record.y)
            for record in point_records
        ],
        crs=parsed_crs,
    )
    frame.to_file(
        Path(output_path),
        layer=LAYER_NAME,
        driver="GPKG",
        index=False,
    )
    return len(point_records)
