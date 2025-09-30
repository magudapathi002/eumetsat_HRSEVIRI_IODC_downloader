from satpy import Scene
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs # type: ignore
import cartopy.feature as cfeature# type: ignore
import os
from datetime import timedelta
from config import settings
import geopandas as gpd

def convert_nat_to_png(product_path: str, output_dir: str):
    """
    Converts all .nat files in a specific product directory to PNG images:
    1. Full India with cloud cover (IR_108 < 273.15K)
    2. Tamil Nadu region only, saved separately in frame_2 folder

    Uses GADM state shapefile for political boundaries.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Search for .nat files in the provided product_path
    files = sorted(glob(os.path.join(product_path, "*.nat")))
    if not files:
        print(f"⚠️ No .nat files found for conversion in {product_path}.")
        return

    try:
        # Load the scene
        scn = Scene(reader='seviri_l1b_native', filenames=files)
        scn.load(['IR_108'])

        # Convert UTC to IST
        utc_time = scn.start_time
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        display_time = ist_time.strftime("%Y-%m-%d %H:%M:%S IST")
        filename_timestamp = ist_time.strftime("%Y%m%d_%H%M%S")

        # Output file path
        out_file = os.path.join(output_dir, f"INDIA_CLOUDS_IST_{filename_timestamp}.png")

        # Resample scene to coarsest area
        scn_resampled = scn.resample(scn.coarsest_area(), resampler='nearest')
        ir_data = scn_resampled['IR_108'].values  # Brightness temp in Kelvin

        # Mask for clouds < 273.15K
        cloud_mask = (ir_data < 273.15) & np.isfinite(ir_data)
        cloud_temp = np.where(cloud_mask, ir_data, np.nan)

        # Get lon/lat
        area = scn_resampled['IR_108'].attrs['area']
        lon, lat = area.get_lonlats()
        lon_flat, lat_flat, temp_flat = lon.flatten(), lat.flatten(), cloud_temp.flatten()
        valid = np.isfinite(temp_flat)

        if not np.any(valid):
            print(f"⚠️ No cloud pixels < 273.15K found in {product_path}. Skipping PNG.")
            return

        # Load shapefile (all Indian states)
        shapefile_path = settings.GEO_JSON
        states_gdf = gpd.read_file(shapefile_path)

        # ---------- PLOT FULL INDIA ----------
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent(settings.REGION_EXTENT, crs=ccrs.PlateCarree())
        ax.coastlines(resolution='10m', color='black', linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
        ax.gridlines(draw_labels=True)

        sc = ax.scatter(
            lon_flat[valid], lat_flat[valid], c=temp_flat[valid], s=0.7,
            transform=ccrs.PlateCarree(), vmin=200, vmax=273.15, cmap='plasma'
        )

        cbar = plt.colorbar(sc, ax=ax)
        cbar.ax.tick_params(labelsize=10)

        # Annotate colorbar with rainfall likelihood labels
        ticks = [230, 235, 265, 273]
        labels = [
            'Heavy rain ,very likely',
            'Moderate rain',
            'Little/no rain',
            ''
        ]
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(labels)

        # State boundaries
        states_gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=1, transform=ccrs.PlateCarree())


        plt.title(f"Rainfall Probablity based of Cloud top temperature\n{display_time}")
        # plt.colorbar(sc, label="Brightness Temperature (K)")
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Saved India PNG: {out_file}")

        # ---------- PLOT TAMIL NADU ONLY ----------
        tn_gdf = states_gdf[states_gdf["NAME_1"] == "Tamil Nadu"]

        if tn_gdf.empty:
            print("⚠️ Tamil Nadu not found in shapefile.")
        else:
            # Load districts shapefile (replace with your actual path or GeoDataFrame)
            districts_shapefile_path = settings.DISTRICTS_GEO_JSON  # Define this in your settings
            districts_gdf = gpd.read_file(districts_shapefile_path)

            tn_districts_gdf = districts_gdf[districts_gdf["NAME_1"] == "Tamil Nadu"]

            frame2_out_dir = settings.FRAME_2_OUTPUT_DIR
            os.makedirs(frame2_out_dir, exist_ok=True)
            frame2_out_file = os.path.join(frame2_out_dir, f"TAMIL_NADU_CLOUDS_IST_{filename_timestamp}.png")

            # Get bounding box of Tamil Nadu
            minx, miny, maxx, maxy = tn_gdf.total_bounds

            # Bigger figure size for better resolution and clarity
            fig2 = plt.figure(figsize=(10, 12))  # was (8, 8)
            ax2 = plt.axes(projection=ccrs.PlateCarree())
            ax2.set_extent([minx, maxx, miny, maxy], crs=ccrs.PlateCarree())
            ax2.coastlines(resolution='10m', color='black', linewidth=1.2)
            ax2.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.8)

            # Improved gridlines
            # gl = ax2.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            # gl.xlabel_style = {'size': 10}
            # gl.ylabel_style = {'size': 10}

            # Filter cloud points within Tamil Nadu bounding box
            mask_lon = (lon_flat >= minx) & (lon_flat <= maxx)
            mask_lat = (lat_flat >= miny) & (lat_flat <= maxy)
            mask_tn = valid & mask_lon & mask_lat

            # Scatter plot with increased size for visibility
            sc2 = ax2.scatter(
                lon_flat[mask_tn], lat_flat[mask_tn], c=temp_flat[mask_tn], s=13,  # increased size
                transform=ccrs.PlateCarree(), vmin=200, vmax=273.15, cmap='plasma'
            )

            # Plot Tamil Nadu boundary
            tn_gdf.boundary.plot(ax=ax2, edgecolor='black', linewidth=1.5, transform=ccrs.PlateCarree())

            # Plot districts boundary with a distinct style
            if not tn_districts_gdf.empty:
                tn_districts_gdf.boundary.plot(
                    ax=ax2, edgecolor='black', linewidth=0.8, linestyle='--', transform=ccrs.PlateCarree()
                )

                # Add district names on the map
                for idx, row in tn_districts_gdf.iterrows():
                    centroid = row.geometry.centroid
                    ax2.text(
                        centroid.x, centroid.y, row["NAME_2"],  # Adjust field name if different
                        fontsize=8, color='black', ha='center', va='center',
                        transform=ccrs.PlateCarree()
                    )

            # Title and colorbar
            plt.title(f"Rainfall Probablity based of Cloud top temperature\n{display_time}", fontsize=14)

            cbar = plt.colorbar(sc2, ax=ax2)
            cbar.ax.tick_params(labelsize=10)

            # Annotate colorbar with rainfall likelihood labels
            ticks = [230, 235, 265, 273]
            labels = [
                'Heavy rain, very likely',
                'Moderate rain',
                'Little/no rain',
                ''
            ]
            cbar.set_ticks(ticks)
            cbar.set_ticklabels(labels)

            # Optionally make labels horizontal and smaller
            for label in cbar.ax.get_yticklabels():
                label.set_fontsize(9)
                label.set_rotation(0)

            plt.savefig(frame2_out_file, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"✅ Saved Tamil Nadu PNG with districts and legend: {frame2_out_file}")
    except Exception as e:
        print(f"❌ Failed to process {product_path}: {e}")