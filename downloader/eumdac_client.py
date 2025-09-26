import subprocess
import datetime as dt
import os
from config import settings

COLLECTION = "EO:EUM:DAT:MSG:HRSEVIRI-IODC"
OUTPUT_DIR = settings.INPUT_DIR

def set_credentials():
    subprocess.run(['eumdac', 'set-credentials', settings.EUMETSAT_KEY, settings.EUMETSAT_SECRET], check=True)
    print("✅ Credentials set successfully.")

def fetch_latest_product():
    """
    Fetch the latest HRSEVIRI-IODC product with a 45-minute buffer.
    Returns the product ID or None.
    """
    set_credentials()

    now = dt.datetime.now(dt.timezone.utc)
    start_time = (now - dt.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
    end_time = (now - dt.timedelta(minutes=45)).strftime('%Y-%m-%dT%H:%M:%S')

    search_cmd = [
        'eumdac', 'search',
        '-c', COLLECTION,
        '-s', start_time,
        '-e', end_time
    ]

    result = subprocess.run(search_cmd, capture_output=True, text=True)
    print(result.stdout)

    lines = result.stdout.strip().split('\n')
    products = [line for line in lines if line.startswith('MSG')]
    if not products:
        print("⚠️ No product found in the search window.")
        return None

    latest_product = products[-1]
    print(f"✅ Latest product available: {latest_product}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    download_cmd = [
        'eumdac', 'download',
        '-c', COLLECTION,
        '-p', latest_product,
        '-o', OUTPUT_DIR
    ]
    try:
        subprocess.run(download_cmd, check=True)
        print(f"📥 Downloaded product: {latest_product}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download product {latest_product}: {e}")
        return None

    return latest_product
