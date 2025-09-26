import os
import zipfile

def extract_product_zip(product_id: str, input_dir: str) -> str | None:
    """
    Extracts the ZIP file for a specific product ID into a directory with the same name.
    Returns the path to the extracted folder, or None if extraction fails.
    """
    if not product_id:
        print("⚠️ No product ID provided for extraction.")
        return None

    zip_filename = f"{product_id}.zip"
    zip_path = os.path.join(input_dir, zip_filename)

    if not os.path.exists(zip_path):
        print(f"❌ ZIP file not found for product: {zip_path}")
        return None

    extract_folder = os.path.join(input_dir, product_id)

    if os.path.exists(extract_folder):
        print(f"ℹ️ Product already extracted: {product_id}")
        return extract_folder

    os.makedirs(extract_folder, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_folder)
        print(f"✅ Extracted ZIP: {zip_filename} → {extract_folder}")
        return extract_folder
    except zipfile.BadZipFile:
        print(f"❌ Failed to extract (corrupt ZIP?): {zip_filename}")
        return None