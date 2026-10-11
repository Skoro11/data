import pandas as pd
import geopandas as gpd

df = pd.read_csv("listings_coords.csv")

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
print(df["dist_to_park_km"].describe())

df.to_csv("park_final.csv", index=False)
print(f"Wrote {len(df)} rows to park_final.csv")
