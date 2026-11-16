"""Chart: containerized freight cost per kg by month, East Coast vs West Coast ports, China imports.

Usage (from the repo root): python3 -I analysis/chart_east_west.py   (run census_combine.py first)
Freight cost per kg = sum of charges / sum of weight across the districts in each coast group.
Gulf ports and inland districts are left out. Whole group averages, so product mix is not held fixed.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = pd.read_csv("data/cleaned/census_china_hs4_by_district.csv", dtype={"DISTRICT": str})
d = d[d.COAST.isin(["East", "West"])]
g = d.groupby(["COAST", "time"])[["CNT_CHA_MO", "CNT_WGT_MO"]].sum()
cpk = (g.CNT_CHA_MO / g.CNT_WGT_MO).unstack(0)
cpk.index = pd.to_datetime(cpk.index)

fig, ax = plt.subplots(figsize=(9, 5))
ax.axvspan(pd.Timestamp("2023-01-01"), pd.Timestamp("2023-10-31"), color="#eeeeee", zorder=0)
ax.text(pd.Timestamp("2023-05-31"), 0.545, "Baseline\nJan to Oct 2023", ha="center", va="top", fontsize=8, color="#666666")
ax.axvline(pd.Timestamp("2023-11-19"), color="#444444", ls="--", lw=1)
ax.text(pd.Timestamp("2023-11-29"), 0.545, "First ship attack\n19 Nov 2023", va="top", fontsize=8, color="#444444")
ax.plot(cpk.index, cpk["East"], color="#c1440e", lw=2.2)
ax.plot(cpk.index, cpk["West"], color="#2a6f97", lw=2.2)
ax.text(cpk.index[-1] + pd.Timedelta(days=12), cpk["East"].iloc[-1] - 0.004, "East Coast", color="#c1440e", fontsize=10, va="center")
ax.text(cpk.index[-1] + pd.Timedelta(days=12), cpk["West"].iloc[-1] + 0.006, "West Coast", color="#2a6f97", fontsize=10, va="center")
ax.set_ylim(0.2, 0.56)
ax.set_xlim(cpk.index[0], cpk.index[-1] + pd.Timedelta(days=95))
ax.set_ylabel("Freight and insurance charges per kg (USD)")
ax.set_title("Freight cost per kg, containerized imports from China\nEast Coast versus West Coast ports, Jan 2022 to Dec 2024", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Source: US Census international trade API (CNT_CHA_MO / CNT_WGT_MO). East: 10 districts, West: 5 districts. Gulf and inland districts excluded.", fontsize=7, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("outputs/freight_per_kg_east_vs_west.png", dpi=150)
print("saved outputs/freight_per_kg_east_vs_west.png")
