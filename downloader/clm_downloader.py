import subprocess
import datetime as dt
import os
from config import settings

CLM_COLLECTION = settings.CLM_COLLECTION
OUTPUT_DIR = settings.CLM_INPUT_DIR

def fetch_latest_clm_product(lookback_minutes=15):
    """
    Fetches the latest CLM product from the last `lookback_minutes`.
    """
    # Reuse credentials setup from the main client if possible, or just run it here.
    # We can assume credentials are set by the main loop or set them here.
    subprocess.run(['eumdac', 'set-credentials', settings.EUMETSAT_KEY, settings.EUMETSAT_SECRET], check=True)
    
    now = dt.datetime.now(dt.timezone.utc)
    # Search window
    start_time = (now - dt.timedelta(minutes=lookback_minutes)).strftime('%Y-%m-%dT%H:%M:%S')
    end_time = now.strftime('%Y-%m-%dT%H:%M:%S')
    
    print(f"🔎 Searching for CLM products between {start_time} and {end_time}...")

    search_cmd = [
        'eumdac', 'search',
        '-c', CLM_COLLECTION,
        '-s', start_time,
        '-e', end_time
    ]

    result = subprocess.run(search_cmd, capture_output=True, text=True)
    
    lines = result.stdout.strip().split('\n')
    # Filter for standard CLM products if needed, though collection should limit it.
    products = [line for line in lines if line.strip()]
    
    if not products:
        print("⚠️ No CLM product found in the search window.")
        return None

    latest_product = products[-1] # usage of -1 implies latest if list is chronological usually
    print(f"✅ Latest CLM product available: {latest_product}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check if we already have it? 
    # eumdac might overwrite or skip. Let's just try download.
    
    download_cmd = [
        'eumdac', 'download',
        '-c', CLM_COLLECTION,
        '-p', latest_product,
        '-o', OUTPUT_DIR
    ]
    
    try:
        subprocess.run(download_cmd, check=True)
        print(f"📥 Downloaded CLM product: {latest_product}")
        return os.path.join(OUTPUT_DIR, latest_product + ".zip") # eumdac downloads as zip usually? 
        # Wait, eumdac download might just be the file itself if it's not a strict bundle
        # For HRSEVIRI it was a Bundle. CLM might be a single GRIB file.
        # usually it downloads as <product_id>.zip or just files.
        # Let's verify what it downloads.
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download CLM product {latest_product}: {e}")
        return None
