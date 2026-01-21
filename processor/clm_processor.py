import pygrib
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import json
from config import settings
import glob

def process_clm_product(product_folder: str, json_out_dir: str, img_out_dir: str):
    """
    Process extracted CLM product folder using pygrib.
    Traverses .grb files, extracts data to JSON, and generates visualization.
    """
    os.makedirs(json_out_dir, exist_ok=True)
    os.makedirs(img_out_dir, exist_ok=True)

    grb_files = sorted(glob.glob(os.path.join(product_folder, "*.grb")))
    if not grb_files:
        print(f"⚠️ No .grb files found in {product_folder}")
        return

    for grb_file in grb_files:
        try:
            print(f"🔄 Processing {grb_file} with pygrib...")
            grbs = pygrib.open(grb_file)
            
            file_basename = os.path.basename(grb_file)
            json_data = {
                "file": file_basename,
                "timestamp": None,
                "messages": []
            }
            
            # Use the first message for plotting if relevant
            plot_msg = None

            # Iterate over messages
            for i, msg in enumerate(grbs):
                print(f"  Msg {i+1}: {msg}")
                
                # Capture timestamp from first message
                if i == 0:
                    try:
                        # Try standard pygrib validDate
                        if hasattr(msg, 'validDate'):
                            valid_date = msg.validDate
                            json_data["timestamp"] = str(valid_date)
                        else:
                            # Fallback: construct from components if available
                            # content is often 'dataDate', 'dataTime'
                            d = str(msg.dataDate)
                            t = f"{msg.dataTime:04d}" # e.g. 1200
                            valid_date = f"{d} {t}"
                            json_data["timestamp"] = valid_date
                    except Exception as e:
                        print(f"  ⚠️ Could not extract date: {e}")
                        valid_date = "Unknown Time"
                        json_data["timestamp"] = None
                    plot_msg = msg
                    plot_date_str = str(valid_date) # Store in local var

                # Extract basic stats
                vals = msg.values
                
                # Safely extract basic stats
                def get_attr(m, key, default="N/A"):
                    # try/except is reliable for pygrib
                    try:
                        return str(m[key])
                    except:
                        return default

                msg_info = {
                    "id": i + 1,
                    "name": get_attr(msg, "name"),
                    "shortName": get_attr(msg, "shortName"),
                    "units": get_attr(msg, "units"),
                    "level": get_attr(msg, "level"),
                    "min": float(np.nanmin(vals)),
                    "max": float(np.nanmax(vals)),
                }
                
                # Debug available keys for the first message
                if i == 0:
                     print(f"  Available keys: {msg.keys()[:10]}...")
                json_data["messages"].append(msg_info)
            
            grbs.close()

            # Save JSON
            json_file = os.path.join(json_out_dir, file_basename + ".json")
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=4)
            print(f"✅ Saved JSON: {json_file}")

            # Visualization
            # Visualization
            if plot_msg:
                try:
                    # Get data and coordinates
                    data = plot_msg.values
                    lats, lons = plot_msg.latlons()

                    # Define India region bounds + margin
                    # REGION_EXTENT = [68, 98, 6, 38]
                    min_lon, max_lon = 60, 100
                    min_lat, max_lat = 0, 45

                    # Create a mask for the region of interest
                    # We need to find the array indices that correspond to this region
                    # Since it's a projection, we can just mask the 2D arrays directly
                    
                    # 1. Mask invalid/space view coordinates first
                    valid_mask = (lats > -90) & (lats < 90) & (lons > -180) & (lons < 360)
                    
                    # 2. Mask to Region
                    region_mask = valid_mask & (lons >= min_lon) & (lons <= max_lon) & (lats >= min_lat) & (lats <= max_lat)
                    
                    if not np.any(region_mask):
                        print("⚠️ No data found in India region.")
                        continue

                    # Optimization: Subset the arrays to the bounding box of the TRUE mask
                    # This keeps the grid structure required for pcolormesh (mostly) 
                    # or we can use scatter with NO stride if the area is small enough.
                    
                    # Actually, pcolormesh expects a mesh. If we just mask, we get a masked array of same shape.
                    # If we simply mask values with NaN, cartopy still transforms the coordinates?
                    # No, we should subset the array indices.
                    
                    rows = np.any(region_mask, axis=1)
                    cols = np.any(region_mask, axis=0)
                    
                    if not np.any(rows) or not np.any(cols):
                         print("⚠️ Region mask empty after row/col check.")
                         continue

                    # Slice the grid
                    rmin, rmax = np.where(rows)[0][[0, -1]]
                    cmin, cmax = np.where(cols)[0][[0, -1]]
                    
                    # Slice with a small margin to be safe
                    # stride = 1 for full resolution (no sprinkles)
                    lats_sub = lats[rmin:rmax+1, cmin:cmax+1]
                    lons_sub = lons[rmin:rmax+1, cmin:cmax+1]
                    data_sub = data[rmin:rmax+1, cmin:cmax+1]

                    print(f"  Subset shape: {data_sub.shape} (from {rmin}:{rmax}, {cmin}:{cmax})")
                    
                    # Handle masked arrays for data
                    if np.ma.is_masked(data_sub):
                        data_sub = data_sub.filled(np.nan)

                    # Larger figure size
                    fig = plt.figure(figsize=(16, 12))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(settings.REGION_EXTENT, crs=ccrs.PlateCarree())
                    ax.coastlines(resolution='10m', color='black', linewidth=1.2)
                    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)
                    
                    # Use pcolormesh on the subset. 
                    # We must ensure lats/lons have no NaNs/Inf even in the subset.
                    # The region_mask filtered range, but 'data_sub' is a square slice, 
                    # so it might include some pixels OUTSIDE the exact mask (e.g. corners) 
                    # which might still be "space view" (nan/inf) ?
                    # Let's check max/min of the subset coords
                    
                    # Sanitize coords
                    # For SCATTER, we can simply flatten and filter invalid coords.
                    # This avoids the "non-finite" pcolormesh error and the "banding" artifact of dummy coords.
                    
                    lats_flat = lats_sub.flatten()
                    lons_flat = lons_sub.flatten()
                    data_flat = data_sub.flatten()
                    
                    # Filter valid coordinates and finite data
                    valid_mask = (lats_flat > -90) & (lats_flat < 90) & \
                                 (lons_flat > -180) & (lons_flat < 360) & \
                                 np.isfinite(data_flat)
                    
                    if not np.any(valid_mask):
                        print("⚠️ No valid data points for scatter.")
                        continue
                        
                    lats_plot = lats_flat[valid_mask]
                    lons_plot = lons_flat[valid_mask]
                    data_plot = data_flat[valid_mask]
                    # Inspect data values to confirm categories
                    # Create custom colormap based on User Request + Standard CLM:
                    # 0: Clear over water (Blue)
                    # 1: Clear over land (Green)
                    # 2: Cloud (White)
                    # 3: No data / Space (Transparent or Black)
                    
                    # DIAGNOSTIC: Calculate and print centroids
                    print("\n--- DIAGNOSTIC: Value Centroids ---")
                    for val in np.unique(data_plot):
                        if np.isnan(val): continue
                        mask = (data_plot == val)
                        count = np.sum(mask)
                        mean_lat = np.mean(lats_plot[mask])
                        mean_lon = np.mean(lons_plot[mask])
                        print(f"  Value {val}: Count={count}, Centroid=({mean_lat:.2f}, {mean_lon:.2f})")
                    print("-----------------------------------\n")

                    # Corrected Colormap based on Standard GRIB CLM Table 4.217 & User Feedback:
                    # 0: Clear over water -> Blue
                    # 1: Clear over land -> Green
                    # 2: Cloud -> White
                    # 3: No data -> Transparent/Black
                    
                    from matplotlib.colors import ListedColormap, BoundaryNorm
                    
                    # Colors:
                    # 0 (Water) -> #1E90FF (DodgerBlue)
                    # 1 (Land)  -> #228B22 (ForestGreen)
                    # 2 (Cloud) -> #FFFFFF (White)
                    # 3 (Space) -> #00000000 (Transparent)
                    
                    colors = ['#1E90FF', '#228B22', '#FFFFFF', '#00000000']
                    cmap_custom = ListedColormap(colors)
                    norm = BoundaryNorm([0, 1, 2, 3, 4], cmap_custom.N)
                    
                    # Scatter with small marker size for dense coverage
                    img = ax.scatter(
                        lons_plot, lats_plot, c=data_plot,
                        transform=ccrs.PlateCarree(),
                        cmap=cmap_custom,
                        norm=norm,
                        s=1.5, 
                        edgecolors='none', 
                        alpha=1.0
                    )
                    
                    # Custom legend
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#1E90FF', edgecolor='k', label='Water (0)'),
                        Patch(facecolor='#228B22', edgecolor='k', label='Land (1)'),
                        Patch(facecolor='#FFFFFF', edgecolor='k', label='Cloud (2)'),
                        Patch(facecolor='#000000', edgecolor='k', label='Space (3)'),
                    ]
                    ax.legend(handles=legend_elements, loc='lower right')
                    
                    title_date = plot_date_str
                    plt.title(f"{plot_msg.name}\n{title_date}", fontsize=16)
                    
                    png_file = os.path.join(img_out_dir, file_basename + ".png")
                    plt.savefig(png_file, bbox_inches='tight', dpi=300)
                    plt.close()
                    print(f"✅ Saved Visualization with Land/Sea/Cloud map: {png_file}")
                except Exception as plot_err:
                     print(f"⚠️ Visualization failed: {plot_err}")
                     import traceback
                     traceback.print_exc()

        except Exception as e:
            print(f"❌ Failed to process {grb_file}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Test block
    from downloader.file_manager import extract_product_zip
    # Needs settings.CLM_INPUT_DIR to be correct.
    # Ex: test_zip_name = "MSG2-SEVI-MSGCLMK-0100-0100-20251220021500.000000000Z-NA"
    # For now, just a placeholder or comment it out if not needed daily.
    # test_zip_name = "MSG2-SEVI-MSGCLMK-0100-0100-20251220021500.000000000Z-NA"
    pass
