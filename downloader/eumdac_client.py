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
    set_credentials()

    now = dt.datetime.now(dt.timezone.utc)
    start_time = (now - dt.timedelta(hours=0,minutes=16)).strftime('%Y-%m-%dT%H:%M:%S')
    end_time = (now - dt.timedelta(minutes=0)).strftime('%Y-%m-%dT%H:%M:%S')
    print(start_time,end_time,"time")

    # Generate 15-minute windows for the past 1 hour
    # for i in range(4):  # 4 intervals in 1 hour
    #     start_time = (now - dt.timedelta(minutes=(60 - i * 15))).strftime('%Y-%m-%dT%H:%M:%S')
    #     end_time = (now - dt.timedelta(minutes=(45 - i * 15))).strftime('%Y-%m-%dT%H:%M:%S')
    #     print(start_time, end_time, "time")
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