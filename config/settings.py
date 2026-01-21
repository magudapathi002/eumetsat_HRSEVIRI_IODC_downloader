import os

# EUMETSAT credentials
EUMETSAT_KEY = os.getenv("EUMETSAT_KEY", "BrETUuWOfkJpKg1QMcqe4PLgbu0a")
EUMETSAT_SECRET = os.getenv("EUMETSAT_SECRET", "NcGkjPq4DhRY05FPfMw_luyMKW0a")
# Collections
HRSEVIRI_COLLECTION = "EO:EUM:DAT:MSG:HRSEVIRI-IODC"
CLM_COLLECTION = "EO:EUM:DAT:MSG:CLM-IODC"
# Paths
INPUT_DIR = "./input"
OUTPUT_DIR = "./frames"
GEO_JSON = "./data/gadm41_IND_shp/gadm41_IND_1.shp"
DISTRICTS_GEO_JSON="./data/gadm41_IND_shp/gadm41_IND_2.shp"
FRAME_2_OUTPUT_DIR = "output/frame_2"
CLM_INPUT_DIR = "./input_clm"
CLM_OUTPUT_DIR = "./output/clm_frames"
JSON_OUTPUT_DIR = "./output/json"

# Region bounds for plotting (India)
REGION_EXTENT = [68, 98, 6, 38]
