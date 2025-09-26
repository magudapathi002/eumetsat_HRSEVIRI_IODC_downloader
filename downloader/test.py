import subprocess
import datetime as dt
import os

# Credentials
CONSUMER_KEY = os.getenv("EUMETSAT_KEY", "BrETUuWOfkJpKg1QMcqe4PLgbu0a")
CONSUMER_SECRET = os.getenv("EUMETSAT_SECRET", "NcGkjPq4DhRY05FPfMw_luyMKW0a")
COLLECTION = "EO:EUM:DAT:MSG:HRSEVIRI"

def set_credentials():
    subprocess.run(['eumdac', 'set-credentials', CONSUMER_KEY, CONSUMER_SECRET], check=True)
    print("✅ Credentials set successfully.")

def download_latest_product():
    # Current UTC time
    now = dt.datetime.utcnow()

    # 45-min buffer to ensure product is ready
    start_time = (now - dt.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
    end_time = (now - dt.timedelta(minutes=45)).strftime('%Y-%m-%dT%H:%M:%S')

    # Search products
    search_cmd = [
        'eumdac', 'search',
        '-c', COLLECTION,
        '-s', start_time,
        '-e', end_time
    ]
    result = subprocess.run(search_cmd, capture_output=True, text=True)
    print(result.stdout)

    # Parse product ID (take the newest)
    lines = result.stdout.strip().split('\n')
    products = [line for line in lines if line.startswith('MSG')]
    if not products:
        print("⚠️ No product found in the search window.")
        return

    latest_product = products[-1]
    print(f"✅ Latest product available: {latest_product}")

    # Download product
    download_cmd = [
        'eumdac', 'download',
        '-c', COLLECTION,
        '-p', latest_product
    ]
    subprocess.run(download_cmd, check=True)
    print(f"📥 Downloaded product: {latest_product}")

if __name__ == "__main__":
    set_credentials()
    download_latest_product()
