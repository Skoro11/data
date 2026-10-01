import numpy as np
import pandas as pd
import rasterio

with rasterio.open("raster/aa16_pm300m_wgs84.tif") as src:
    data = src.read(1)
    nodata = src.nodata
    rows, cols = np.where(data != nodata)
    lons, lats = rasterio.transform.xy(src.transform, rows, cols)
    pm2_5 = data[rows, cols]

df = pd.DataFrame({"longitude": lons, "latitude": lats, "pm2_5": pm2_5})

print(f"Wrote {len(df)} grid cells covering NYC (longitude, latitude, pm2_5)")
df.to_csv("air_quality.csv", index=False)
