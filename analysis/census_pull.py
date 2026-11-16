"""Step 2. Pull monthly HS4 imports for the chosen origins, one small file per month and country.

Usage (from the repo root):
  export CENSUS_API_KEY=your_key
  python3 -I analysis/census_pull.py --test      # one month, one country, prints the head
  python3 -I analysis/census_pull.py             # full pull, safe to rerun, skips finished files
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


def fetch(month, cty):
    fields = [C.COMMODITY_VAR, C.COUNTRY_VAR, C.DISTRICT_VAR] + list(C.MEASURES.values())
    q = {"get": ",".join(fields), "time": month, C.COMM_LEVEL_PARAM: C.COMM_LEVEL,
         C.COUNTRY_VAR: cty, C.COMMODITY_VAR: "*", C.DISTRICT_VAR: "*", "key": key}
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


os.makedirs(C.RAW_DIR, exist_ok=True)
test = "--test" in sys.argv
todo = [("2023-10", "5700")] if test else [(m, c) for m in months(C.START_MONTH, C.END_MONTH) for c in C.COUNTRIES]
for month, cty in todo:
    path = os.path.join(C.RAW_DIR, f"hs4_{cty}_{month}.csv")
    if os.path.exists(path) and not test:
        continue
    rows = fetch(month, cty)
    if rows is None:
        print("FAILED", month, cty); continue
    if test:
        print(len(rows), "rows"); [print(r) for r in rows[:5]]
        if "--save" not in sys.argv:
            break
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print("saved", path, len(rows) - 1 if rows else 0, "rows")
    time.sleep(0.3)
