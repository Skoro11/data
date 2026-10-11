import pandas as pd

# Row 0 is the real header, row 1 is a descriptive sub-header (not data) - skip it.
df = pd.read_csv("raw/median_income_raw.csv", skiprows=[1])

# GEO_ID looks like "1400000US36005000100": "1400000US" is the Census code for
# "this is a tract-level geography", followed by the actual 11-digit GEOID.
df["GEOID"] = df["GEO_ID"].str[9:]

# Suppressed tracts show up as "-" (text) instead of a number; coercing to
# numeric turns those into a proper NaN instead of a literal dash string.
df["median_income"] = pd.to_numeric(df["B19013_001E"], errors="coerce")

out = df[["GEOID", "NAME", "median_income"]]

missing = out["median_income"].isna().sum()
print(f"{missing} of {len(out)} tracts have no median_income (suppressed)")

out.to_csv("median_income_tract.csv", index=False)
print(f"Wrote {len(out)} rows to median_income_tract.csv")
