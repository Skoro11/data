import geopandas as gpd
import pandas as pd

df = pd.read_csv("final_dataset.csv", dtype={"GEOID": str})
print(f"Starting rows: {len(df)}")

# --- home_status (scope filter, moved here from mapper.py) ---
print("\n--- home_status ---")
print(df["home_status"].value_counts(dropna=False))

before = len(df)
df = df[df["home_status"] == "RECENTLY_SOLD"]
after = len(df)
print(f"home_status filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, not RECENTLY_SOLD)")

df = df.drop(columns=["home_status"])  # done its job, not a model feature

# --- NYC boundary (scope filter, moved here from mapper.py) ---
print("\n--- NYC boundary ---")
boundaries = gpd.read_file("Borough_Boundaries.geojson")
points = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"]), crs=boundaries.crs
)
nyc_points = gpd.sjoin(points, boundaries, how="inner", predicate="within")

before = len(df)
df = df[df.index.isin(nyc_points.index)]
after = len(df)
print(f"NYC boundary filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, outside NYC)")

# --- type ---
print("\n--- type ---")
print(df["type"].value_counts(dropna=False))

before = len(df)
df = df[df["type"] != "MULTI_FAMILY"]
after = len(df)
print(f"\ntype filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, MULTI_FAMILY had too few examples)")

# --- sold_price ---
print("\n--- sold_price ---")
missing = df["sold_price"].isna().sum()
out_of_range = (df["sold_price"].notna() & ((df["sold_price"] < 100_000) | (df["sold_price"] > 2_000_000))).sum()
print(f"Missing: {missing}, outside $100k-$2M range: {out_of_range}")

before = len(df)
df = df[df["sold_price"].notna() & (df["sold_price"] >= 100_000) & (df["sold_price"] <= 2_000_000)]
after = len(df)
print(f"sold_price filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/out-of-range sold_price)")

# --- sqft ---
print("\n--- sqft ---")
missing = df["sqft"].isna().sum()
zero = (df["sqft"] == 0).sum()
outliers = (df["sqft"] > 10_000).sum()
print(f"Missing: {missing}, zero: {zero}, outliers (>10,000): {outliers}")

before = len(df)
df = df[df["sqft"].notna() & (df["sqft"] > 0) & (df["sqft"] <= 10_000)]
after = len(df)
print(f"sqft filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/zero/outlier sqft)")

# --- beds ---
print("\n--- beds ---")
missing = df["beds"].isna().sum()
zero = (df["beds"] == 0).sum()
implausible = (df["sqft"] / df["beds"] < 100).sum()
print(f"Missing: {missing}, zero: {zero}, implausible sqft/beds ratio (<100): {implausible}")

before = len(df)
df = df[df["beds"].notna() & (df["beds"] > 0) & (df["sqft"] / df["beds"] >= 100)]
after = len(df)
print(f"beds filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/zero beds or implausible sqft/beds ratio)")

# --- baths ---
print("\n--- baths ---")
missing = df["baths"].isna().sum()
zero = (df["baths"] == 0).sum()
implausible = ((df["baths"] - df["beds"]) > 3).sum()
print(f"Missing: {missing}, zero: {zero}, implausible (baths exceed beds by >3): {implausible}")

before = len(df)
df = df[df["baths"].notna() & (df["baths"] > 0) & ((df["baths"] - df["beds"]) <= 3)]
after = len(df)
print(f"baths filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/zero baths or implausible baths-vs-beds)")

# --- zip_code ---
print("\n--- zip_code ---")
bad_zips = ["02110", "10512", "10803", "11003", "11040", "11243", "13214", "14068", "2110"]
found = df["zip_code"].astype(str).isin(bad_zips).sum()
print(f"Known non-NYC/corrupted zip codes found: {found}")

before = len(df)
df = df[~df["zip_code"].astype(str).isin(bad_zips)]
after = len(df)
print(f"zip_code filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, known non-NYC/corrupted zip codes)")

# --- latitude / longitude ---
print("\n--- latitude / longitude ---")
missing = df["latitude"].isna().sum() + df["longitude"].isna().sum()
print(f"Missing (combined): {missing}")

before = len(df)
df = df[df["latitude"].notna() & df["longitude"].notna()]
after = len(df)
print(f"latitude/longitude filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing coordinates)")

# --- sale_year ---
print("\n--- sale_year ---")
missing = df["sale_year"].isna().sum()
invalid = (~df["sale_year"].isin([2024, 2025, 2026])).sum()
print(f"Missing: {missing}, outside 2024-2026: {invalid}")

before = len(df)
df = df[df["sale_year"].isin([2024, 2025, 2026])]
after = len(df)
print(f"sale_year filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/invalid sale_year)")

# --- url ---
print("\n--- url ---")
missing = df["url"].isna().sum()
dupes = df["url"].duplicated().sum()
print(f"Missing: {missing}, duplicates: {dupes}")

before = len(df)
df = df[df["url"].notna()]
df = df[~df["url"].duplicated()]
after = len(df)
print(f"url filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/duplicate url)")

# --- image_url ---
print("\n--- image_url ---")
missing = df["image_url"].isna().sum()
no_photo = (df["image_url"] == "no photo").sum()
print(f"Missing: {missing}, 'no photo' placeholder (not an error, kept): {no_photo}")

before = len(df)
df = df[df["image_url"].notna()]
after = len(df)
print(f"image_url filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing image_url)")

# --- nearest_station_name / dist_to_subway_km ---
print("\n--- nearest_station_name / dist_to_subway_km ---")
missing = df["nearest_station_name"].isna().sum() + df["dist_to_subway_km"].isna().sum()
print(f"Missing (combined): {missing}")

before = len(df)
df = df[df["nearest_station_name"].notna() & df["dist_to_subway_km"].notna()]
after = len(df)
print(f"subway filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing subway match)")

# --- dist_to_cbd_km ---
print("\n--- dist_to_cbd_km ---")
missing = df["dist_to_cbd_km"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["dist_to_cbd_km"].notna()]
after = len(df)
print(f"dist_to_cbd_km filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing dist_to_cbd_km)")

# --- nearest_park_name / dist_to_park_km ---
print("\n--- nearest_park_name / dist_to_park_km ---")
missing = df["nearest_park_name"].isna().sum() + df["dist_to_park_km"].isna().sum()
print(f"Missing (combined): {missing}")

before = len(df)
df = df[df["nearest_park_name"].notna() & df["dist_to_park_km"].notna()]
after = len(df)
print(f"park filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing park match)")

# --- GEOID ---
print("\n--- GEOID ---")
missing = df["GEOID"].isna().sum()
bad_format = (df["GEOID"].astype(str).str.len() != 11).sum()
print(f"Missing: {missing}, wrong format (not 11 digits): {bad_format}")

before = len(df)
df = df[df["GEOID"].notna() & (df["GEOID"].astype(str).str.len() == 11)]
after = len(df)
print(f"GEOID filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/malformed GEOID)")

# --- median_income ---
print("\n--- median_income ---")
missing = df["median_income"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["median_income"].notna()]
after = len(df)
print(f"median_income filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, suppressed/missing tract income)")

# --- pm2_5 ---
print("\n--- pm2_5 ---")
missing = df["pm2_5"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["pm2_5"].notna()]
after = len(df)
print(f"pm2_5 filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, outside raster coverage)")

# --- mean_felony ---
print("\n--- mean_felony ---")
missing = df["mean_felony"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["mean_felony"].notna()]
after = len(df)
print(f"mean_felony filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing mean_felony)")

df.to_csv("final_dataset_clean.csv", index=False)
print(f"\nWrote {len(df)} rows to final_dataset_clean.csv")
