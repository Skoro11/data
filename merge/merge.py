import geopandas as gpd
import pandas as pd

base = pd.read_csv("../starting_point/dataset_mapped.csv")
print(f"Base listings: {len(base)}")

# --- per-listing files, joined on listing_id ---
air_quality = pd.read_csv("../air_quality/air_quality_distance_final.csv", usecols=["listing_id", "pm2_5"])
base = base.merge(air_quality, on="listing_id", how="left")

subway = pd.read_csv(
    "../subway/subway_distance_final.csv",
    usecols=["listing_id", "nearest_station_name", "dist_to_subway_km"],
)
base = base.merge(subway, on="listing_id", how="left")

distances = pd.read_csv(
    "../distance_to/distance_to_final.csv",
    usecols=["listing_id", "dist_to_cbd_km", "nearest_park_name", "dist_to_park_km"],
)
base = base.merge(distances, on="listing_id", how="left")

# --- tract-level files, joined via a spatial join to get each listing's GEOID ---
tracts = gpd.read_file("../median_income/2020_Census_Tracts_20261004.geojson")
tracts = tracts.rename(columns={"geoid": "GEOID"})[["GEOID", "geometry"]]

points = gpd.GeoDataFrame(
    base,
    geometry=gpd.points_from_xy(base["longitude"], base["latitude"]),
    crs="EPSG:4326",
)
joined = gpd.sjoin(points, tracts, how="left", predicate="within")
base["GEOID"] = joined["GEOID"].values

missing_geoid = base["GEOID"].isna().sum()
print(f"{missing_geoid} listings did not match a census tract")

median_income = pd.read_csv("../median_income/median_income_final.csv", dtype={"GEOID": str})[
    ["GEOID", "median_income"]
]
base = base.merge(median_income, on="GEOID", how="left")

crime = pd.read_csv("../crime/crime_final.csv", dtype={"GEOID": str})[["GEOID", "mean_felony"]]
base = base.merge(crime, on="GEOID", how="left")

print(f"Final merged dataset: {len(base)} rows, {len(base.columns)} columns")
print(base.columns.tolist())

base.to_csv("final_dataset.csv", index=False)
print("Wrote final_dataset.csv")
