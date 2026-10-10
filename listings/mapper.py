import pandas as pd


df = pd.read_csv("zillow_raw_dataset.csv", encoding="utf-8-sig", low_memory=False)

########## MAPPING ##################
# This script only selects/renames/cleans fields into a consistent schema.
# No rows are dropped here - all scope filtering (status, price range,
# NYC boundary, sale year) happens later, in merge/clean.py, alongside
# the data-quality filtering, so every filtering decision lives in one place.

# clean up sold_price here since it needs parsing before it can be a column:
# "$739,000" -> 739000, "$1.45M" -> 1450000
price = df["soldPrice"].str.replace("$", "", regex=False).str.replace(",", "", regex=False)
is_millions = price.str.endswith("M")
price = price.str.rstrip("M").astype(float)
price[is_millions] = price[is_millions] * 1_000_000
df["sold_price_clean"] = price

# Extract fields for cleaner dataset
mapped = pd.DataFrame()
# home_status is kept only so merge/clean.py can filter to RECENTLY_SOLD;
# it is dropped again at the end of clean.py since it's not a model feature.
mapped["home_status"] = df["hdpData/homeInfo/homeStatus"]
mapped["type"] = df["hdpData/homeInfo/homeType"]
mapped["sold_price"] = df["sold_price_clean"]
mapped["sqft"] = df["hdpData/homeInfo/livingArea"]
# Fill empty columns with fallback values from another column that have same value
mapped["beds"] = df["beds"].fillna(df["hdpData/homeInfo/bedrooms"])
mapped["baths"] = df["baths"].fillna(df["hdpData/homeInfo/bathrooms"])
mapped["zip_code"] = df["addressZipcode"].fillna(df["hdpData/homeInfo/zipcode"])
mapped["latitude"] = df["latLong/latitude"]
mapped["longitude"] = df["latLong/longitude"]
mapped["sale_year"] = pd.to_datetime(df["hdpData/homeInfo/dateSold"], unit="ms").dt.year
mapped["url"] = df["detailUrl"]
# Build a direct link to the first photo (baseUrl is a template like
# ".../{photoKey}-p_e.jpg"); listings without one get "no photo"
mapped["image_url"] = [
    base.replace("{photoKey}", key) if pd.notna(base) and pd.notna(key) else "no photo"
    for base, key in zip(
        df["carouselPhotosComposable/baseUrl"],
        df["carouselPhotosComposable/photoData/0/photoKey"],
    )
]

# Drop rows with missing coordinates - this isn't a scope/quality judgment
# call like the filters in clean.py, it's a hard structural requirement:
# every downstream enrichment script does geospatial math (distance,
# nearest-neighbor) that simply cannot run on a NaN coordinate.
before_coords = len(mapped)
mapped = mapped[mapped["latitude"].notna() & mapped["longitude"].notna()]
after_coords = len(mapped)
print(f"Coordinate presence check: {before_coords} -> {after_coords} rows "
      f"({before_coords - after_coords} dropped as missing latitude/longitude)")

# Stable unique id for each listing - needed since multiple listings can share
# the exact same latitude/longitude (e.g. different units in the same building),
# so later enrichment merges must join on this id, not on lat/long or row order.
mapped = mapped.reset_index(drop=True)
mapped.insert(0, "listing_id", mapped.index)

# Save the dataset
mapped.to_csv("zillow_mapped_dataset.csv", index=False)
print(f"Wrote {len(mapped)} rows to zillow_mapped_dataset.csv")

# Lightweight coordinates-only file - every enrichment script needs just
# listing_id/latitude/longitude, so this is the one shared, duplicated source
# for that subset instead of each script re-extracting it from the full file.
mapped[["listing_id", "latitude", "longitude"]].to_csv("listings_coords.csv", index=False)
print(f"Wrote {len(mapped)} rows to listings_coords.csv")
