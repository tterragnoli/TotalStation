# Total Station GeoPackage

Read a total station points CSV, report duplicate IDs, missing values, invalid
numeric values, and anomalous elevations per code, then export records with
valid X and Y coordinates to a GeoPackage.

## Requirements

Python 3.10 or later. The commands below use Windows PowerShell. The coordinate
reference system (CRS) must be provided explicitly for every run.

## Installation

Open PowerShell in the project folder, then create and activate a virtual
environment and install the project with its test dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

If PowerShell blocks environment activation, use the virtual environment's
Python directly for installation, execution, and tests:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m totalstation_gpkg.cli examples\points.csv points.gpkg --crs EPSG:32632
.\.venv\Scripts\python.exe -m pytest
```

## Usage

With the virtual environment activated, run the included sample:

```powershell
python -m totalstation_gpkg.cli examples\points.csv points.gpkg --crs EPSG:32632
```

The required CSV columns are `id`, `x`, `y`, `z`, and `codice`. The input
header must retain `codice` because it is part of the specified source format.
The CSV must be UTF-8 with a header row and comma delimiters. X, Y, and Z must
use a period as the decimal separator.

To process another file, replace the input and output paths and provide the
CRS that matches your survey data:

```powershell
python -m totalstation_gpkg.cli path\to\survey.csv path\to\output.gpkg --crs EPSG:XXXX
```

The output GeoPackage contains a `points` layer. Replace `EPSG:XXXX` with the
correct CRS identifier; the example uses `EPSG:32632`.

The CLI prints validation findings to the console. Blank IDs are reported as
missing and are not treated as duplicates. Elevations are evaluated separately
for each code using valid numeric values: an elevation is anomalous when its
modified MAD score exceeds 3.5 in absolute value; groups with fewer than five
valid elevations are not evaluated. If a group's MAD is zero, every elevation
that differs from the median is reported. Records with valid X and Y are
exported; records without them remain in the report but are excluded from the
GeoPackage. Exported attributes retain the source column names, including
`codice`; a missing or invalid Z is stored as an empty attribute.

## Tests

```powershell
python -m pytest
```
