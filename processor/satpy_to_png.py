from satpy import Scene
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs # type: ignore
import cartopy.feature as cfeature# type: ignore
import os
from datetime import timedelta
from config import settings

def convert_nat_to_png(product_path: str, output_dir: str):
    """
    Converts all .nat files in a specific product directory to a single PNG image.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Search for .nat files only in the provided product_path
    files = sorted(glob(os.path.join(product_path, "*.nat")))
    if not files:
        print(f"⚠️ No .nat files found for conversion in {product_path}.")
        return

    # Process all .nat files as a single scene
    try:
        scn = Scene(reader='seviri_l1b_native', filenames=files)
        scn.load(['IR_108'])

        # Get timestamp and convert to IST
        utc_time = scn.start_time
        ist_time = utc_time + timedelta(hours=5, minutes=30)

        # Format for display and filename
        display_time = ist_time.strftime("%Y-%m-%d %H:%M:%S IST")
        filename_timestamp = ist_time.strftime("%Y%m%d_%H%M%S")

        out_file = os.path.join(output_dir, f"INDIA_CLOUDS_IST_{filename_timestamp}.png")

        # Resample and process data
        scn_resampled = scn.resample(scn.coarsest_area(), resampler='nearest')
        ir_data = scn_resampled['IR_108'].values
        ir_data_celsius = ir_data - 273.15

        # Create a mask for clouds (temperature < 0°C)
        cloud_mask = (ir_data_celsius < 0) & np.isfinite(ir_data_celsius)
        cloud_temp = np.where(cloud_mask, ir_data_celsius, np.nan)

        area = scn_resampled['IR_108'].attrs['area']
        lon, lat = area.get_lonlats()
        lon_flat, lat_flat, temp_flat = lon.flatten(), lat.flatten(), cloud_temp.flatten()
        valid = np.isfinite(temp_flat)

        if not np.any(valid):
            print(f"⚠️ No cloud pixels < 0°C found in {product_path}. Skipping PNG.")
            return

        # Plotting
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent(settings.REGION_EXTENT, crs=ccrs.PlateCarree())
        ax.coastlines(resolution='10m', color='black', linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
        ax.gridlines(draw_labels=True)

        sc = ax.scatter(
            lon_flat[valid], lat_flat[valid], c=temp_flat[valid], s=0.7, transform=ccrs.PlateCarree(),
            vmin=-73.15, vmax=0
        )

        plt.title(f"Cloud Cover over India (IR_108 < 0°C)\n{display_time}")
        plt.colorbar(sc, label="Brightness Temperature (°C)")
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved PNG: {out_file}")

    except Exception as e:
        print(f"❌ Failed to process {product_path}: {e}")