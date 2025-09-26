import os

# EUMETSAT credentials
EUMETSAT_KEY = os.getenv("EUMETSAT_KEY", "BrETUuWOfkJpKg1QMcqe4PLgbu0a")
EUMETSAT_SECRET = os.getenv("EUMETSAT_SECRET", "NcGkjPq4DhRY05FPfMw_luyMKW0a")

# Paths
INPUT_DIR = "./input"
OUTPUT_DIR = "./frames"

# Region bounds for plotting (India)
REGION_EXTENT = [68, 98, 6, 38]
