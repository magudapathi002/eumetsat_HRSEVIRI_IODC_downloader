import os

# EUMETSAT credentials
EUMETSAT_KEY = os.getenv("EUMETSAT_KEY", "BrETUuWOfkJpKg1QMcqe4PLgbu0a")
EUMETSAT_SECRET = os.getenv("EUMETSAT_SECRET", "NcGkjPq4DhRY05FPfMw_luyMKW0a")

# Paths
INPUT_DIR = "./input"
OUTPUT_DIR = "./frames"
GEO_JSON = "./data/gadm41_IND_shp/gadm41_IND_1.shp"
DISTRICTS_GEO_JSON="./data/gadm41_IND_shp/gadm41_IND_2.shp"
FRAME_2_OUTPUT_DIR = "output/frame_2"

# Region bounds for plotting (India)
REGION_EXTENT = [68, 98, 6, 38]
