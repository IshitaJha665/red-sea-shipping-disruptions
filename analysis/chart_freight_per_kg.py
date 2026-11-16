"""Step 1 chart: freight cost per kg, China, Oct 2023, top 10 HS4 products by containerized value.

Usage (from the repo root): python3 -I analysis/chart_freight_per_kg.py
DISTRICT == "-" is the national total row for each product, so we use only those rows.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAMES = {"9503": "Toys", "8471": "Computers", "8507": "Batteries", "9504": "Video games",
         "8708": "Vehicle parts", "8516": "Electric appliances", "8528": "Monitors and TVs",
         "3924": "Plastic household goods", "9401": "Seats", "9505": "Festive articles",
         "9403": "Furniture", "3926": "Other plastic articles"}

df = pd.read_csv("data/raw/census/monthly_files/hs4_5700_2023-10.csv", dtype=str)
df = df.loc[:, ~df.columns.duplicated()]
df = df[df.DISTRICT == "-"].copy()
for c in ["CNT_CHA_MO", "CNT_WGT_MO", "CNT_VAL_MO"]:
    df[c] = pd.to_numeric(df[c])
df = df[df.CNT_WGT_MO > 0]
df["cost_per_kg"] = df.CNT_CHA_MO / df.CNT_WGT_MO
top = df.nlargest(10, "CNT_VAL_MO").sort_values("cost_per_kg")
labels = [f"{NAMES.get(c, 'HS ' + c)} ({c})" for c in top.I_COMMODITY]

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(labels, top.cost_per_kg, color="#2a6f97")
for y, v in enumerate(top.cost_per_kg):
    ax.text(v + 0.01, y, f"${v:.2f}", va="center", fontsize=9)
ax.set_xlabel("Freight and insurance charges per kg (USD)")
ax.set_title("Containerized freight cost per kg, imports from China, Oct 2023\nTop 10 HS4 products by containerized value", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlim(0, top.cost_per_kg.max() * 1.15)
fig.text(0.01, 0.01, "Source: US Census international trade API (CNT_CHA_MO / CNT_WGT_MO)", fontsize=7, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("outputs/freight_per_kg_china_oct2023.png", dpi=150)
print("saved outputs/freight_per_kg_china_oct2023.png")
