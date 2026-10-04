import geopandas as gpd
import pandas as pd

tracts = gpd.read_file("2020_Census_Tracts_20261004.geojson")
tracts = tracts.rename(columns={"geoid": "GEOID"})[["GEOID", "geometry"]]

tract_population = pd.read_csv("population_tract.csv", dtype={"GEOID": str})
tracts = tracts.merge(tract_population[["GEOID", "population"]], on="GEOID", how="left")

missing = tracts["population"].isna().sum()
print(f"{missing} of {len(tracts)} tracts have no population (left empty)")

out = tracts.drop(columns="geometry")
out.to_csv("population_final.csv", index=False)
print(f"Wrote {len(out)} rows to population_final.csv")
