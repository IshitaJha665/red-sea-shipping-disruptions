"""Step 3. Build the HS4 panel and SeaShare from the raw monthly files.

Usage (from the repo root):  python3 -I analysis/census_clean.py
Writes data/cleaned/census_hs4_panel.csv and data/cleaned/sea_share_hs4_2022.csv
"""
import glob, os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_config as C

raw = os.environ.get("CENSUS_RAW_DIR", C.RAW_DIR)
out = os.environ.get("CENSUS_OUT_DIR", "data/cleaned")
os.makedirs(out, exist_ok=True)
M = C.MEASURES
frames = [pd.read_csv(p, dtype=str) for p in sorted(glob.glob(os.path.join(raw, "hs4_*.csv")))]
if not frames:
    sys.exit("No raw files found in " + raw)
df = pd.concat(frames, ignore_index=True)
df = df.rename(columns={C.COMMODITY_VAR: "hs4", C.COUNTRY_VAR: "origin", C.DISTRICT_VAR: "district", "time": "month"})
for k, v in M.items():
    df[k] = pd.to_numeric(df[v], errors="coerce")

# SeaShare by product from 2022: containerized vessel value over total import value
y22 = df[df["month"].str.startswith("2022")]
g = y22.groupby("hs4")[["cnt_value", "gen_value"]].sum()
g["sea_share"] = g["cnt_value"] / g["gen_value"].replace(0, np.nan)
g[["sea_share"]].to_csv(os.path.join(out, "sea_share_hs4_2022.csv"))

# Panel Jan 2023 to Dec 2024
p = df[(df["month"] >= "2023-01") & (df["month"] <= C.END_MONTH)].copy()
p = p[(p["charges"] > 0) & (p["weight"] > 0) & (p["gen_value"] > 0)]
p["freight_per_kg"] = p["charges"] / p["weight"]
p["value_per_kg"] = p["gen_value"] / p["weight"]
p["landed_per_kg"] = (p["gen_value"] + p["charges"]) / p["weight"]
p["ln_fc"] = np.log(p["freight_per_kg"])
p["ln_value_per_kg"] = np.log(p["value_per_kg"])
p = p.merge(g[["sea_share"]], left_on="hs4", right_index=True, how="left")
cols = ["month", "origin", "district", "hs4", "freight_per_kg", "value_per_kg", "landed_per_kg",
        "ln_fc", "ln_value_per_kg", "sea_share"]
p[cols].to_csv(os.path.join(out, "census_hs4_panel.csv"), index=False)
print("panel rows:", len(p), "| products:", p["hs4"].nunique(), "| months:", p["month"].nunique())
