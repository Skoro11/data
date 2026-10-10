import numpy as np
import pandas as pd
import geopandas as gpd

EARTH_RADIUS_KM = 6371

df = pd.read_csv("listings_coords.csv")

# --- distance to CBD (Times Square) ---
center = pd.read_csv("city_center.csv").iloc[0]
CBD_LAT, CBD_LON = center["latitude"], center["longitude"]

lat1, lon1 = np.radians(df["latitude"]), np.radians(df["longitude"])
lat2, lon2 = np.radians(CBD_LAT), np.radians(CBD_LON)

dlat = lat2 - lat1
dlon = lon2 - lon1
a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
c = 2 * np.arcsin(np.sqrt(a))
df["dist_to_cbd_km"] = EARTH_RADIUS_KM * c

# --- distance to nearest park ---
parks = gpd.read_file("Parks_Properties_20261007.geojson")
parks = parks[["name311", "geometry"]].to_crs(epsg=2263)

points = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326",
).to_crs(epsg=2263)

nearest = gpd.sjoin_nearest(points, parks, distance_col="dist_ft")
nearest = nearest[~nearest.index.duplicated(keep="first")]

df["nearest_park_name"] = nearest["name311"].values
df["dist_to_park_km"] = nearest["dist_ft"].values * 0.0003048

print(f"Processed {len(df)} listings")
print(df[["dist_to_cbd_km", "dist_to_park_km"]].describe())

df.to_csv("distance_to_final.csv", index=False)
print(f"Wrote {len(df)} rows to distance_to_final.csv")
