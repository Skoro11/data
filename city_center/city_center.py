import numpy as np
import pandas as pd

EARTH_RADIUS_KM = 6371

# Times Square - reference point for "distance to CBD"
CBD_LAT, CBD_LON = 40.758, -73.9855

df = pd.read_csv("listings_coords.csv")

lat1, lon1 = np.radians(df["latitude"]), np.radians(df["longitude"])
lat2, lon2 = np.radians(CBD_LAT), np.radians(CBD_LON)

dlat = lat2 - lat1
dlon = lon2 - lon1
a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
c = 2 * np.arcsin(np.sqrt(a))
df["dist_to_cbd_km"] = EARTH_RADIUS_KM * c

print(f"Processed {len(df)} listings")
print(df["dist_to_cbd_km"].describe())

df.to_csv("city_center_final.csv", index=False)
print(f"Wrote {len(df)} rows to city_center_final.csv")
