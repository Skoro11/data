import pandas as pd
import rasterio

with rasterio.open("raster/aa16_pm300m_wgs84.tif") as src:
    nodata = src.nodata
    listings = pd.read_csv("listings_coords.csv")

    coords = zip(listings["longitude"], listings["latitude"])
    listings["pm2_5"] = [val[0] for val in src.sample(coords)]
    listings.loc[listings["pm2_5"] == nodata, "pm2_5"] = pd.NA

missing = listings["pm2_5"].isna().sum()
print(f"PM2.5 lookup: {len(listings)} listings, {missing} fell outside the raster coverage (no value assigned)")

listings.to_csv("air_quality.csv", index=False)
print(f"Wrote {len(listings)} rows to air_quality.csv")
