import geopandas as gpd
import pandas as pd

YEARS = 2  # 2024 + 2025

crimes = pd.read_csv("NYPD_Complaint_Data_Historic_20261004 (2).csv", low_memory=False)
crimes = crimes.dropna(subset=["Latitude", "Longitude"])
crimes["Latitude"] = crimes["Latitude"].astype(str).str.replace(",", ".").astype(float)
crimes["Longitude"] = crimes["Longitude"].astype(str).str.replace(",", ".").astype(float)

points = gpd.GeoDataFrame(
    crimes,
    geometry=gpd.points_from_xy(crimes["Longitude"], crimes["Latitude"]),
    crs="EPSG:4326",
)

tracts = gpd.read_file("2020_Census_Tracts_20261004.geojson")
tracts = tracts.rename(columns={"geoid": "GEOID"})[["GEOID", "geometry"]]

joined = gpd.sjoin(points, tracts, how="left", predicate="within")

counts = joined.groupby("GEOID").size().reset_index(name="felony_count")
counts["mean_felony"] = counts["felony_count"] / YEARS

centroids = tracts.geometry.to_crs(epsg=2263).centroid.to_crs(epsg=4326)
tracts["longitude"] = centroids.x
tracts["latitude"] = centroids.y

out = tracts.drop(columns="geometry").merge(counts[["GEOID", "mean_felony"]], on="GEOID", how="left")
out["mean_felony"] = out["mean_felony"].fillna(0)

unmatched = len(points) - joined["GEOID"].notna().sum()
print(f"{unmatched} of {len(points)} incidents did not fall inside any tract")

out.to_csv("crime_final.csv", index=False)
print(f"Wrote {len(out)} rows to crime_final.csv")
