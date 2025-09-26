from satpy import Scene
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
from datetime import timedelta
from matplotlib.colors import LinearSegmentedColormap

INPUT_DIR = "./input"
OUTPUT_DIR = "./frames"

def convert_nat_to_png(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    
    # Recursive search for .nat files in all subdirectories
    files = sorted(glob(os.path.join(input_dir, "**", "*.nat"), recursive=True))
    if not files:
        print("⚠️ No .nat files found for conversion.")
        return

    for file in files:
        timestamp = os.path.splitext(os.path.basename(file))[0]
        out_file = os.path.join(output_dir, f"IR_108_clouds_india_{timestamp}.png")
        
        if os.path.exists(out_file):
            print(f"⏭ Already processed: {out_file}")
            continue

        try:
            scn = Scene(reader='seviri_l1b_native', filenames=[file])
            scn.load(['IR_108'])

            utc_time = scn.start_time

            # Add 5 hours 30 minutes
            ist_time = utc_time + timedelta(hours=5, minutes=30)

            # Format as string
            times = ist_time.strftime("%Y-%m-%d %H:%M:%S")

            scn_resampled = scn.resample(scn.coarsest_area(), resampler='nearest')
            ir_data = scn_resampled['IR_108'].values
            ir_data_celsius = ir_data - 273.15

            cloud_mask = (ir_data_celsius < 0) & np.isfinite(ir_data_celsius)
            cloud_temp = np.where(cloud_mask, ir_data_celsius, np.nan)

            area = scn_resampled['IR_108'].attrs['area']
            lon, lat = area.get_lonlats()
            lon_flat, lat_flat, temp_flat = lon.flatten(), lat.flatten(), cloud_temp.flatten()
            valid = np.isfinite(temp_flat)

            if not np.any(valid):
                print(f"⚠️ No cloud pixels < 0°C found in {file}. Skipping PNG.")
                continue

            fig = plt.figure(figsize=(12, 8))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_extent([68, 98, 6, 38], crs=ccrs.PlateCarree())
            # ax.add_feature(cfeature.OCEAN, facecolor='blue', zorder=0)
            # ax.add_feature(cfeature.LAND, facecolor='green', zorder=0)
            ax.coastlines(resolution='10m', color='black', linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
            ax.gridlines(draw_labels=True)

            sc = ax.scatter(
                lon_flat[valid], lat_flat[valid], c=temp_flat[valid], s=0.7, transform=ccrs.PlateCarree(),
                vmin=-73.15, vmax=0
            )

            plt.title(f"Cloud Cover over India and Heat signature (IR_108 < 0°C)\n{times}")
            plt.colorbar(sc, label="Brightness Temperature (°C)")
            plt.savefig(out_file, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"✅ Saved PNG: {out_file}")

        except Exception as e:
            print(f"❌ Failed to process {file}: {e}")
