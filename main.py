import os
from apscheduler.schedulers.blocking import BlockingScheduler
from downloader.eumdac_client import fetch_latest_product
from processor.satpy_to_png import convert_nat_to_png
from downloader.file_manager import extract_product_zip
from config import settings

os.makedirs(settings.INPUT_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

def download_and_process():
    print("⏳ Checking for latest product...")
    product_id = fetch_latest_product()
    if not product_id:
        print("⚠️ No new product available at this time.")
        return

    # Extract the specific product ZIP
    product_path = extract_product_zip(product_id, settings.INPUT_DIR)

    if not product_path:
        print(f"❌ Failed to extract product {product_id}, skipping processing.")
        return

    # Convert .nat → PNG from the specific product folder
    convert_nat_to_png(product_path, settings.OUTPUT_DIR)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(
        download_and_process,
        'interval',
        minutes=15,
        id='download_and_process',
    )

    print("🚀 Scheduler started: fetching HRSEVIRI-IODC every 15 minutes...")
    # The scheduler will run the job once immediately on start,
    # and then every 15 minutes.
    scheduler.start()
