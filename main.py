import os
from apscheduler.schedulers.blocking import BlockingScheduler
from downloader.eumdac_client import fetch_latest_product
from processor.satpy_to_png import convert_nat_to_png
from downloader.file_manager import extract_zip_files
from config import settings

os.makedirs(settings.INPUT_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True) 

def download_and_process():
    print("⏳ Checking for latest product...")
    product = fetch_latest_product()
    if not product:
        print("⚠️ No new product available at this time.")
        return

    # Extract any ZIPs
    extract_zip_files(settings.INPUT_DIR)

    # Convert .nat → PNG
    convert_nat_to_png(settings.INPUT_DIR, settings.OUTPUT_DIR)

if __name__ == "__main__":
    # Run once immediately
    download_and_process()

    # Schedule every 15 minutes
    scheduler = BlockingScheduler()
    scheduler.add_job(
        download_and_process,
        'interval',
        minutes=15,
        id='download_and_process',
        next_run_time=None
    )

    print("🚀 Scheduler started: fetching HRSEVIRI-IODC every 15 minutes...")
    scheduler.start()
