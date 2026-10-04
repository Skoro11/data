import pandas as pd

nyc_zips = pd.read_csv("zip_codes.csv", dtype={"zip_code": str})["zip_code"].tolist()

df = pd.read_excel(
    "NewYork_DemographicsByZipCode_sample.xlsx",
    sheet_name="2024AmericanCommunitySurvey",
    header=4,
    dtype={"name": str},
)

out = df[df["name"].isin(nyc_zips)][["name", "population"]].rename(
    columns={"name": "zip_code"}
)
out = out.sort_values("zip_code")

out.to_csv("population_zip.csv", index=False)
print(f"Wrote {len(out)} rows to population_zip.csv")
