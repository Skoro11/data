import geopandas as gpd
import pandas as pd

tracts = gpd.read_file("2020_Census_Tracts_20261004.geojson")
tracts = tracts.rename(columns={"geoid": "GEOID"})[["GEOID", "geometry"]]

tract_income = pd.read_csv("median_income_tract.csv", dtype={"GEOID": str})
tracts = tracts.merge(tract_income[["GEOID", "median_income"]], on="GEOID", how="left")

missing = tracts["median_income"].isna().sum()
print(f"{missing} of {len(tracts)} tracts have no median_income (left empty)")

out = tracts.drop(columns="geometry")
out.to_csv("median_income_final.csv", index=False)
print(f"Wrote {len(out)} rows to median_income_final.csv")
