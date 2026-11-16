"""Combine the monthly Census files into one table. Raw files are read, never changed.

Usage (from the repo root): python3 -I analysis/census_combine.py
Writes data/cleaned/census_china_hs4_by_district.csv (district rows) and, once the 2022 national
files exist, data/cleaned/census_china_hs4_national.csv (national totals, DISTRICT "-").
"""
import glob, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_config as C

KEEP = ["I_COMMODITY", "CTY_CODE", "DISTRICT", "CNT_CHA_MO", "CNT_WGT_MO", "CNT_VAL_MO", "GEN_VAL_MO", "time"]
NUM = ["CNT_CHA_MO", "CNT_WGT_MO", "CNT_VAL_MO", "GEN_VAL_MO"]


def read(f):
    d = pd.read_csv(f, dtype=str)
    d = d.loc[:, ~d.columns.duplicated()]
    return d[KEEP]


def finish(d):
    d[NUM] = d[NUM].apply(pd.to_numeric)
    return d.sort_values(["time", "DISTRICT", "I_COMMODITY"]).reset_index(drop=True)


os.makedirs("data/cleaned", exist_ok=True)
coast = {**{k: "East" for k in C.EAST_COAST}, **{k: "Gulf" for k in C.GULF_COAST}, **{k: "West" for k in C.WEST_COAST}}

files = [f for f in glob.glob(os.path.join(C.MONTHLY_DIR, "hs4_5700_d*.csv"))
         if re.fullmatch(r"hs4_5700_d\d+_\d{4}-\d{2}\.csv", os.path.basename(f))]
d = finish(pd.concat([read(f) for f in files], ignore_index=True))
d.insert(3, "COAST", d.DISTRICT.map(coast))
d.to_csv("data/cleaned/census_china_hs4_by_district.csv", index=False)
print("district file:", len(files), "raw files,", len(d), "rows,", d.time.min(), "to", d.time.max())

nat = [f for f in glob.glob(os.path.join(C.MONTHLY_DIR, "hs4_5700_20??-??.csv"))]
if nat:
    n = finish(pd.concat([read(f) for f in nat], ignore_index=True))
    n = n[n.DISTRICT == "-"]
    n.to_csv("data/cleaned/census_china_hs4_national.csv", index=False)
    print("national file:", len(nat), "raw files,", len(n), "rows,", n.time.min(), "to", n.time.max())
