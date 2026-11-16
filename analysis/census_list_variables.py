"""Step 1. Download the variable list and print names and labels that matter.

Usage (from the repo root):  python3 -I analysis/census_list_variables.py
Saves data/raw/census/variables.json.
"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_config as C

url = C.BASE_URL + "/variables.json"
with urllib.request.urlopen(url, timeout=60) as r:
    data = json.load(r)
os.makedirs(C.RAW_DIR, exist_ok=True)
with open(os.path.join(C.RAW_DIR, "variables.json"), "w") as f:
    json.dump(data, f, indent=1)
keys = ("CHARGE", "WGT", "WEIGHT", "CNT", "VES", "CIF", "GEN_VAL", "COMM", "CTY", "DIST", "TIME", "LVL")
for name, meta in sorted(data["variables"].items()):
    label = meta.get("label", "")
    if any(k in name.upper() or k in label.upper() for k in keys):
        print(f"{name:28s} {label}")
print("\nNow open analysis/census_config.py and make MEASURES match these names.")
