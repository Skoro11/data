import geopandas as gpd
import pandas as pd

parks = gpd.read_file("Parks_Properties_20261007.geojson")
parks = parks[["name311", "geometry"]].to_crs(epsg=2263)

pd.read_csv("../starting_point/dataset_mapped.csv", usecols=["latitude", "longitude"]).to_csv(
    "listings.csv", index=False
)
listings = pd.read_csv("listings.csv")
points = gpd.GeoDataFrame(
    listings,
    geometry=gpd.points_from_xy(listings["longitude"], listings["latitude"]),
    crs="EPSG:4326",
).to_crs(epsg=2263)

nearest = gpd.sjoin_nearest(points, parks, distance_col="dist_ft")
nearest = nearest[~nearest.index.duplicated(keep="first")]

listings["nearest_park_name"] = nearest["name311"].values
listings["dist_to_park_km"] = nearest["dist_ft"].values * 0.0003048

print(f"Matched {len(listings)} listings to nearest park")
print(listings["dist_to_park_km"].describe())

listings.to_csv("park_distance_final.csv", index=False)
print(f"Wrote {len(listings)} rows to park_distance_final.csv")
