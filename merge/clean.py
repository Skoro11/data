import geopandas as gpd
import pandas as pd

df = pd.read_csv("final_dataset.csv", dtype={"GEOID": str})
print(f"Starting rows: {len(df)}")

# --- NYC boundary (scope filter, based on census tract match) ---
# GEOID was already computed in merge.py via a spatial join against the
# census tract boundaries; a missing GEOID means the listing fell outside
# every tract, which is treated as outside NYC (same geography used
# throughout, instead of a separate Borough Boundaries file).
print("\n--- NYC boundary ---")

before = len(df)
df = df[df["GEOID"].notna()]
after = len(df)
print(f"NYC boundary filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, outside NYC / no matching census tract)")

# --- home_status (scope filter, moved here from mapper.py) ---
print("\n--- home_status ---")
print(df["home_status"].value_counts(dropna=False))

before = len(df)
df = df[df["home_status"] == "RECENTLY_SOLD"]
after = len(df)
print(f"home_status filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, not RECENTLY_SOLD)")

df = df.drop(columns=["home_status"])  # done its job, not a model feature

# --- sold_price (precautionary re-check of the Apify scraper's own price-range filter) ---
print("\n--- sold_price ---")
missing = df["sold_price"].isna().sum()
out_of_range = (df["sold_price"].notna() & ((df["sold_price"] < 100_000) | (df["sold_price"] > 2_000_000))).sum()
print(f"Missing: {missing}, outside $100k-$2M range: {out_of_range}")

before = len(df)
df = df[df["sold_price"].notna() & (df["sold_price"] >= 100_000) & (df["sold_price"] <= 2_000_000)]
after = len(df)
print(f"sold_price filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/out-of-range sold_price)")

# --- sale_year (precautionary re-check of the Apify scraper's own date-range filter) ---
print("\n--- sale_year ---")
missing = df["sale_year"].isna().sum()
invalid = (~df["sale_year"].isin([2024, 2025, 2026])).sum()
print(f"Missing: {missing}, outside 2024-2026: {invalid}")

before = len(df)
df = df[df["sale_year"].isin([2024, 2025, 2026])]
after = len(df)
print(f"sale_year filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/invalid sale_year)")

# --- non-residential type (precautionary re-check of the Apify scraper's
# own residential-only search filter; none of these categories were found
# anywhere in the raw dataset, confirming the scraper-side filter worked) ---
print("\n--- non-residential type ---")
non_residential = ["LAND", "LOT", "MANUFACTURED", "TOWNHOUSE"]
found = df["type"].isin(non_residential).sum()
print(f"Non-residential categories found: {found}")

before = len(df)
df = df[~df["type"].isin(non_residential)]
after = len(df)
print(f"non-residential type filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, Lots/Land, Manufactured, or Townhomes)")

# --- type ---
print("\n--- type ---")
counts = df["type"].value_counts(dropna=False)
pct = df["type"].value_counts(dropna=False, normalize=True) * 100
print(pd.concat([counts, pct.round(2)], axis=1, keys=["count", "pct"]))

before = len(df)
df = df[df["type"] != "MULTI_FAMILY"]
after = len(df)
print(f"\ntype filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, MULTI_FAMILY had too few examples)")

# --- dist_to_cbd_km ---
print("\n--- dist_to_cbd_km ---")
missing = df["dist_to_cbd_km"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["dist_to_cbd_km"].notna()]
after = len(df)
print(f"dist_to_cbd_km filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing dist_to_cbd_km)")

# sanity check: closest/furthest listing from the CBD, used to spot-check the
# haversine calculation against known NYC geography (Midtown vs. Tottenville)
print(f"CBD reference point (Times Square): (40.758, -73.9855)")
closest = df.loc[df["dist_to_cbd_km"].idxmin()]
furthest = df.loc[df["dist_to_cbd_km"].idxmax()]
print(f"Closest to CBD: listing_id {closest['listing_id']}, {closest['dist_to_cbd_km']:.3f} km "
      f"({closest['latitude']}, {closest['longitude']})")
print(f"Furthest from CBD: listing_id {furthest['listing_id']}, {furthest['dist_to_cbd_km']:.3f} km "
      f"({furthest['latitude']}, {furthest['longitude']})")

# --- mean_felony ---
print("\n--- mean_felony ---")
missing = df["mean_felony"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["mean_felony"].notna()]
after = len(df)
print(f"mean_felony filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing mean_felony)")

# --- pm2_5 ---
print("\n--- pm2_5 ---")
missing = df["pm2_5"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["pm2_5"].notna()]
after = len(df)
print(f"pm2_5 filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, outside raster coverage)")

# --- median_income ---
print("\n--- median_income ---")
missing = df["median_income"].isna().sum()
print(f"Missing: {missing}")

before = len(df)
df = df[df["median_income"].notna()]
after = len(df)
print(f"median_income filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, suppressed/missing tract income)")

# --- sqft ---
# lower bound of 120 sqft is grounded in law rather than a round number:
# NY Multiple Dwelling Law §214 (CONDO/APARTMENT) and IRC §R304 (basis for
# SINGLE_FAMILY construction) both require every dwelling unit to contain
# at least one habitable room of >=120 sqft. A unit smaller than that
# cannot legally contain its own mandatory room, so it is treated as a
# data entry error rather than a genuine residence.
print("\n--- sqft ---")
missing = df["sqft"].isna().sum()
zero = (df["sqft"] == 0).sum()
outliers_low = ((df["sqft"] > 0) & (df["sqft"] < 120)).sum()
outliers_high = (df["sqft"] > 9_999).sum()
print(f"Missing: {missing}, zero: {zero}, "
      f"outliers (<120): {outliers_low}, outliers (>9,999): {outliers_high}")

# distribution in 100-sqft bins, so the chosen thresholds can be eyeballed
# against the actual shape of the data rather than picked blind
bins = list(range(0, 10_100, 100)) + [float("inf")]
labels = [f"{b}-{b+99}" for b in bins[:-2]] + ["10000+"]
binned = pd.cut(df["sqft"], bins=bins, labels=labels, right=False)
print("\nsqft distribution (100-sqft bins):")
print(binned.value_counts().sort_index().to_string())

before = len(df)
dropped_missing = df["sqft"].isna().sum()
dropped_zero = (df["sqft"] == 0).sum()
dropped_outliers_low = ((df["sqft"] > 0) & (df["sqft"] < 120)).sum()
dropped_outliers_high = (df["sqft"] > 9_999).sum()
df = df[df["sqft"].notna() & (df["sqft"] >= 120) & (df["sqft"] <= 9_999)]
after = len(df)
print(f"\nDropped breakdown: missing={dropped_missing}, zero={dropped_zero}, "
      f"outliers (<120)={dropped_outliers_low}, outliers (>9,999)={dropped_outliers_high}, "
      f"total dropped={before - after} ({100*(before-after)/before:.2f}%)")
print(f"sqft filter: {before} -> {after} rows")

# --- beds ---
print("\n--- beds ---")
missing = df["beds"].isna().sum()
zero = (df["beds"] == 0).sum()

# legally-grounded plausibility check instead of an arbitrary ratio: NY
# Multiple Dwelling Law §214 and IRC §R304 both require a dwelling unit's
# first room to have >=120 sqft and every additional room >=70 sqft, so
# sqft below that sum cannot legally contain the reported number of beds
min_required_sqft = 120 + 70 * (df["beds"] - 1)
implausible = (df["beds"] > 0) & (df["sqft"] < min_required_sqft)
print(f"Missing: {missing}, zero: {zero}, "
      f"implausible (sqft below 120+70*(beds-1)): {implausible.sum()}")

before = len(df)
df = df[df["beds"].notna() & (df["beds"] > 0) & (df["sqft"] >= min_required_sqft)]
after = len(df)
print(f"beds filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/zero beds or implausible beds-vs-sqft)")

# --- baths ---
print("\n--- baths ---")
missing = df["baths"].isna().sum()
zero = (df["baths"] == 0).sum()
print(f"Missing: {missing}, zero: {zero}")

before = len(df)
df = df[df["baths"].notna() & (df["baths"] > 0)]
after = len(df)
print(f"baths filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/zero baths)")

# --- nearest_station_name / dist_to_subway_km ---
print("\n--- nearest_station_name / dist_to_subway_km ---")
missing = df["nearest_station_name"].isna().sum() + df["dist_to_subway_km"].isna().sum()
print(f"Missing (combined): {missing}")

before = len(df)
df = df[df["nearest_station_name"].notna() & df["dist_to_subway_km"].notna()]
after = len(df)
print(f"subway filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing subway match)")

# --- nearest_park_name / dist_to_park_km ---
print("\n--- nearest_park_name / dist_to_park_km ---")
missing = df["nearest_park_name"].isna().sum() + df["dist_to_park_km"].isna().sum()
print(f"Missing (combined): {missing}")

before = len(df)
df = df[df["nearest_park_name"].notna() & df["dist_to_park_km"].notna()]
after = len(df)
print(f"park filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing park match)")

# --- year_built ---
# placed last so the missing/implausible count reflects only listings that
# otherwise survive every other filter - the smallest, most precise set
# worth fixing (e.g. re-scraping) rather than wasting effort on rows that
# would be dropped anyway for unrelated reasons (sqft, beds, baths, etc.)
print("\n--- year_built ---")
missing = df["year_built"].isna().sum()
too_old = (df["year_built"].notna() & (df["year_built"] < 1700)).sum()
built_after_sold = (df["year_built"].notna() & (df["year_built"] > df["sale_year"])).sum()
print(f"Missing: {missing}, implausibly old (<1700): {too_old}, built after sold: {built_after_sold}")

before = len(df)
df = df[df["year_built"].notna() & (df["year_built"] >= 1700) & (df["year_built"] <= df["sale_year"])]
after = len(df)
print(f"year_built filter: {before} -> {after} rows "
      f"({before - after} dropped, {100*(before-after)/before:.2f}%, missing/implausible year_built)")

# age (sale_year - year_built) replaces raw year_built as the model feature;
# building age at the time of sale is the economically meaningful signal,
# not the calendar year itself, and year_built would be collinear with it anyway
df["age"] = df["sale_year"] - df["year_built"]
df = df.drop(columns=["year_built"])

df.to_csv("final_dataset_clean.csv", index=False)
print(f"\nWrote {len(df)} rows to final_dataset_clean.csv")
