import os
from apscheduler.schedulers.blocking import BlockingScheduler
from downloader.eumdac_client import fetch_latest_product
from processor.satpy_to_png import convert_nat_to_png
from processor.satpy_to_png import convert_nat_to_png
from processor.clm_processor import process_clm_product
from downloader.clm_downloader import fetch_latest_clm_product
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

def download_and_process_clm():
    print("⏳ Checking for latest CLM product...")
    product_id = fetch_latest_clm_product() # Returns path if downloaded: input/prod.zip
    
    if not product_id:
        print("⚠️ No new CLM product available.")
        return

    # Extract - fetch_latest_clm_product returns path to zip
    # We need product_id relative to input dir? 
    # fetch_latest_clm_product returns absolute path to zip file.
    # extract_product_zip expects product_id and input_dir.
    # But product_id is just the name. 
    # Let's adjust or parse from path.
    
    zip_path = product_id
    zip_name = os.path.basename(zip_path)
    product_name = os.path.splitext(zip_name)[0]
    
    # extract_product_zip logic: expects product_id as the name, and looks in input_dir (settings.INPUT_DIR or CLM_INPUT_DIR)
    # Re-using extract_product_zip(product_id, dir)
    
    extracted_path = extract_product_zip(product_name, settings.CLM_INPUT_DIR)
    
    if not extracted_path:
         print("❌ Failed to extract CLM.")
         return

    process_clm_product(extracted_path, settings.JSON_OUTPUT_DIR, settings.CLM_OUTPUT_DIR)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(
        download_and_process,
        'interval',
        minutes=15,
        id='download_and_process',
        max_instances=2
    )
    scheduler.add_job(
        download_and_process_clm,
        'interval',
        minutes=15,
        id='download_and_process_clm',
        max_instances=2
    )
    print("🚀 Scheduler started: fetching HRSEVIRI-IODC and CLM every 15 minutes...")

    download_and_process()
    download_and_process_clm()

    scheduler.start()
