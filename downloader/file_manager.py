import os
import zipfile

def extract_zip_files(input_dir="./input"):
    """
    Extract all ZIP files in the input directory.
    Skips files already extracted.
    """
    zip_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".zip")]

    if not zip_files:
        print("⚠️ No ZIP files found to extract.")
        return

    for zip_file in zip_files:
        zip_path = os.path.join(input_dir, zip_file)
        extract_folder = os.path.join(input_dir, os.path.splitext(zip_file)[0])

        if os.path.exists(extract_folder):
            print(f"ℹ️ ZIP already extracted: {zip_file}")
            continue

        os.makedirs(extract_folder, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_folder)
            print(f"✅ Extracted ZIP: {zip_file} → {extract_folder}")
        except zipfile.BadZipFile:
            print(f"❌ Failed to extract (corrupt ZIP?): {zip_file}")
