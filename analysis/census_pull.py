"""Step 2. Pull monthly HS4 imports for the chosen origins, one small file per month and country.

Usage (from the repo root):
  export CENSUS_API_KEY=your_key
  python3 -I analysis/census_pull.py --test      # one month, one country, prints the head
  python3 -I analysis/census_pull.py             # full pull, safe to rerun, skips finished files
  python3 -I analysis/census_pull.py --from 2023-11 --to 2023-11 --countries 5700 --districts 27   # one district, one month
  python3 -I analysis/census_pull.py --from 2022-01 --to 2024-12 --countries 5700 --districts coasts --workers 4   # East, Gulf, West ports
  python3 -I analysis/census_pull.py --from 2023-11 --to 2024-02 --countries 5700 --national   # a few months, China only, national totals (much smaller request)
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_config as C

key = os.environ.get("CENSUS_API_KEY")
if not key:
    sys.exit("Set CENSUS_API_KEY first (free key: api.census.gov/data/key_signup.html)")


def months(a, b):
    y, m = map(int, a.split("-")); y2, m2 = map(int, b.split("-"))
    while (y, m) <= (y2, m2):
        yield f"{y}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def fetch(month, cty, district="*"):
    fields = [C.COMMODITY_VAR, C.COUNTRY_VAR, C.DISTRICT_VAR] + list(C.MEASURES.values())
    q = {"get": ",".join(fields), "time": month, C.COMM_LEVEL_PARAM: C.COMM_LEVEL,
         C.COUNTRY_VAR: cty, C.COMMODITY_VAR: "*", C.DISTRICT_VAR: "-" if "--national" in sys.argv else district, "key": key}
    url = C.BASE_URL + "?" + urllib.parse.urlencode(q, safe=",*")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                body = r.read().decode()
            return json.loads(body) if body.strip() else []
        except Exception as e:
            print("retry", month, cty, e)
            time.sleep(3 * (attempt + 1))
    return None


os.makedirs(C.MONTHLY_DIR, exist_ok=True)
test = "--test" in sys.argv
def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


# Optional: --from 2023-11 --to 2024-02 --countries 5700,5830 limits the full pull
a, b = arg("--from") or C.START_MONTH, arg("--to") or C.END_MONTH
ctys = arg("--countries").split(",") if arg("--countries") else list(C.COUNTRIES)
# --districts 27,10 (or --districts coasts) pulls one small file per district, month and country
dsel = arg("--districts")
if dsel == "coasts":
    dists = list(C.EAST_COAST) + list(C.GULF_COAST) + list(C.WEST_COAST)
elif dsel:
    dists = dsel.split(",")
else:
    dists = None
span = "--span" in sys.argv   # one request per district covering the whole --from to --to range
if test:
    todo = [("2023-10", "5700", "*")]
elif dists and span:
    todo = [(f"from {a} to {b}", c, d) for c in ctys for d in dists]
elif dists:
    todo = [(m, c, d) for m in months(a, b) for c in ctys for d in dists]
else:
    todo = [(m, c, "*") for m in months(a, b) for c in ctys]
def one(job):
    month, cty, dist = job
    tag = f"_d{dist}" if dist != "*" else ""
    path = os.path.join(C.MONTHLY_DIR, f"hs4_{cty}{tag}_{month.replace('from ', '').replace(' to ', '_to_')}.csv")
    if os.path.exists(path) and not test:
        return
    rows = fetch(month, cty, dist)
    if rows is None:
        print("FAILED", month, cty, dist, flush=True); return
    if test:
        print(len(rows), "rows"); [print(r) for r in rows[:5]]
        if "--save" not in sys.argv:
            return
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print("saved", path, len(rows) - 1 if rows else 0, "rows", flush=True)


# --span asks for all months of a district in one request (fewer, bigger requests).
# --workers 4 sends several requests at once (default 1). Rerun after any FAILED line.
workers = int(arg("--workers") or 1)
if workers > 1 and not test:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, todo))
else:
    for job in todo:
        one(job)
        time.sleep(0.3)
