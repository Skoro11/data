import numpy as np
import pandas as pd
import rasterio

with rasterio.open("raster/aa16_pm300m_wgs84.tif") as src:
    data = src.read(1)
    nodata = src.nodata
    rows, cols = np.where(data != nodata)
    lons, lats = rasterio.transform.xy(src.transform, rows, cols)
    pm2_5 = data[rows, cols]

    grid = pd.DataFrame({"longitude": lons, "latitude": lats, "pm2_5": pm2_5})
    print(f"Wrote {len(grid)} grid cells covering NYC (longitude, latitude, pm2_5)")
    grid.to_csv("air_quality.csv", index=False)

    pd.read_csv("../listings/listings_coords.csv").to_csv("listings.csv", index=False)
    listings = pd.read_csv("listings.csv")

    coords = zip(listings["longitude"], listings["latitude"])
    listings["pm2_5"] = [val[0] for val in src.sample(coords)]
    listings.loc[listings["pm2_5"] == nodata, "pm2_5"] = pd.NA

missing = listings["pm2_5"].isna().sum()
print(f"PM2.5 lookup: {len(listings)} listings, {missing} fell outside the raster coverage (no value assigned)")

listings.to_csv("air_quality_distance_final.csv", index=False)
print(f"Wrote {len(listings)} rows to air_quality_distance_final.csv")
