"""Panama versus Suez: how big and how long was each shock, relative to the Jan to Oct 2023 baseline.

Usage: python3 -I analysis/panama_vs_suez.py data/raw data/cleaned outputs
Inputs (in data/raw): Container_Shipping_Data.xlsx (PortWatch monthly transits, USEC services),
                      Container Transit Data.xlsx (Clarksons monthly transits and TEU)
Outputs: data/cleaned/transits_monthly_clean.csv, outputs/panama_vs_suez_summary.csv,
         outputs/usec_routing_split_dec2023.csv
"""
import sys, os
import openpyxl
import pandas as pd

raw, cleaned, out = sys.argv[1:4]
BASE = ("2023-01", "2023-10")  # baseline window, Oct 2023 is the reference month


def sheet_table(wb, name, key):
    rows = list(wb[name].iter_rows(values_only=True))
    i = [k for k, r in enumerate(rows) if r[0] == key][0]
    return pd.DataFrame(rows[i + 1:], columns=rows[i])


# PortWatch counts of containership transits
wb = openpyxl.load_workbook(os.path.join(raw, "Container_Shipping_Data.xlsx"), data_only=True)
pw = sheet_table(wb, "Transits_Monthly", "Month")
pw = pw[pw["Month"].astype(str).str.startswith("20")].set_index("Month")
cols = {
    "Suez": "Suez – containership transits",
    "Cape": "Cape of Good Hope – containership transits",
    "Panama": "Panama – containership transits",
    "BabElMandeb": "Bab el-Mandeb – containership transits",
}
pw = pw[[v for v in cols.values()]].astype(float)
pw.columns = list(cols.keys())
pw.to_csv(os.path.join(cleaned, "transits_monthly_clean.csv"))

# Clarksons Panama and Suez TEU (thousand)
cw = openpyxl.load_workbook(os.path.join(raw, "Container Transit Data.xlsx"), data_only=True)


def clarksons(name):
    rows = list(cw[name].iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:]).iloc[:, :5]
    df.columns = ["Date", "c1", "c2", "c3", "c4"]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    return df.set_index("Month")


pan, suez = clarksons("Panama"), clarksons("Suez")
teu = pd.DataFrame({"Panama_TEU_k": pan["c4"].astype(float), "Suez_TEU_k": suez["c4"].astype(float)})

base = pw.loc[BASE[0]:BASE[1]].mean()
tbase = teu.loc[BASE[0]:BASE[1]].mean()
rows = []
for m in ["2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-06", "2024-09", "2024-12"]:
    r = {"Month": m}
    for c in pw.columns:
        r[c + "_count"] = pw.loc[m, c]
        r[c + "_pct_vs_baseline"] = round(100 * (pw.loc[m, c] / base[c] - 1), 1)
    for c in teu.columns:
        r[c + "_pct_vs_baseline"] = round(100 * (teu.loc[m, c] / tbase[c] - 1), 1)
    rows.append(r)
summ = pd.DataFrame(rows)
summ.to_csv(os.path.join(out, "panama_vs_suez_summary.csv"), index=False)
print("Baseline means (counts), Jan to Oct 2023:\n", base.round(1).to_string())
print("Baseline means (TEU thousand):\n", tbase.round(1).to_string())
print(summ.T.to_string(header=False))

# USEC routing split, Dec 2023 snapshot
u = sheet_table(wb, "USEC_Services", "Period / network year").dropna(subset=["Service"])
snap = u[u["Period / network year"].astype(str).str.startswith("Dec 2023")].copy()
snap["TEU"] = pd.to_numeric(snap["Weekly capacity (TEU)"], errors="coerce")
split = snap.groupby("Routing")["TEU"].agg(["count", "sum"]).rename(columns={"count": "services", "sum": "weekly_TEU"})
split["share_pct"] = (100 * split["weekly_TEU"] / split["weekly_TEU"].sum()).round(1)
split.to_csv(os.path.join(out, "usec_routing_split_dec2023.csv"))
print(split.to_string())
print("Total weekly TEU in snapshot:", split["weekly_TEU"].sum())
