import pandas as pd

stops = pd.read_csv("stops.txt")

stations = stops[stops["location_type"] == 1]

out = stations[["stop_name", "stop_lat", "stop_lon"]].rename(
    columns={"stop_lat": "latitude", "stop_lon": "longitude"}
)

out.to_csv("subway_stations.csv", index=False)
print(f"Wrote {len(out)} subway stations to subway_stations.csv")
