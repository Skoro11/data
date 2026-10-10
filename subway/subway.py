import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

stops = pd.read_csv("stops.txt")

stations = stops[stops["location_type"] == 1]

stations = stations[["stop_name", "stop_lat", "stop_lon"]].rename(
    columns={"stop_lat": "latitude", "stop_lon": "longitude"}
)
stations.to_csv("subway_stations.csv", index=False)
print(f"Wrote {len(stations)} subway stations to subway_stations.csv")

listings = pd.read_csv("listings_coords.csv")

EARTH_RADIUS_KM = 6371
stations_rad = np.radians(stations[["latitude", "longitude"]].values)
listings_rad = np.radians(listings[["latitude", "longitude"]].values)

tree = BallTree(stations_rad, metric="haversine")
dist, idx = tree.query(listings_rad, k=1)

listings["nearest_station_name"] = stations.iloc[idx.flatten()]["stop_name"].values
listings["dist_to_subway_km"] = dist.flatten() * EARTH_RADIUS_KM

print(f"Matched {len(listings)} listings to nearest subway station")
print(listings["dist_to_subway_km"].describe())

listings.to_csv("subway_distance_final.csv", index=False)
print(f"Wrote {len(listings)} rows to subway_distance_final.csv")
