"""Configuration settings for CSV validation and GeoPackage export."""

# Column names required in the input CSV header.
REQUIRED_COLUMNS = ("id", "x", "y", "z", "codice")

# Column names that must contain numeric values.
NUMERIC_COLUMNS = ("x", "y", "z")

# Absolute modified MAD score above which an elevation is anomalous.
MAD_THRESHOLD = 3.5

# Minimum number of valid elevations required to evaluate a code group.
MIN_GROUP_SIZE = 5

# GeoPackage layer name used for exported points.
LAYER_NAME = "points"

# Elevations within this many units of the group median are not anomalous.
HEIGHT_TOLERANCE = 0.02
