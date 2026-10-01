import pandas as pd
import geopandas as gpd



df = pd.read_csv("zillow_raw_dataset.csv", encoding="utf-8-sig", low_memory=False)

############## FILTERING ########################

# statusType says "SOLD" for every row, but homeStatus shows some are
# actually still PENDING - keep only genuinely completed sales
before_status = len(df)
df = df[df["hdpData/homeInfo/homeStatus"] == "RECENTLY_SOLD"]
after_status = len(df)
print(f"Status filter: {before_status} -> {after_status} rows "
      f"({before_status - after_status} dropped as not RECENTLY_SOLD)")

# clean up sold_price early so it travels with df through the filters below:
# "$739,000" -> 739000, "$1.45M" -> 1450000
price = df["soldPrice"].str.replace("$", "", regex=False).str.replace(",", "", regex=False)
is_millions = price.str.endswith("M")
price = price.str.rstrip("M").astype(float)
price[is_millions] = price[is_millions] * 1_000_000
df["sold_price_clean"] = price

# safety check: scraper should only return $100k-$2M, but re-filter just in case
before_price = len(df)
df = df[(df["sold_price_clean"] >= 100_000) & (df["sold_price_clean"] <= 2_000_000)]
after_price = len(df)
print(f"Price filter: {before_price} -> {after_price} rows "
      f"({before_price - after_price} dropped as outside $100k-$2M)")

# Filter based on boundaries
before_boundary = len(df)
boundaries = gpd.read_file("Borough_Boundaries.geojson")

points = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["latLong/longitude"], df["latLong/latitude"]),
    crs=boundaries.crs,
)

nyc_points = gpd.sjoin(points, boundaries, how="inner", predicate="within")

df = nyc_points.drop(columns=["geometry", "index_right"])
after_boundary = len(df)
print(f"Boundary filter: {before_boundary} -> {after_boundary} rows "
      f"({before_boundary - after_boundary} dropped as outside NYC)")


########## MAPPING ##################

# Extract fields for cleaner dataset
mapped = pd.DataFrame()
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

# safety check: scraper should only return 2024-2026 sales, but re-filter just in case
before_year = len(mapped)
mapped = mapped[mapped["sale_year"].isin([2024, 2025, 2026])]
after_year = len(mapped)
print(f"Year filter: {before_year} -> {after_year} rows "
      f"({before_year - after_year} dropped as outside 2024-2026)")

# Save the dataset
mapped.to_csv("dataset_mapped.csv", index=False)
print(f"Wrote {len(mapped)} rows to dataset_mapped.csv")
