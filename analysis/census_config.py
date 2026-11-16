"""Settings shared by the Census scripts. Edit here, not in the scripts.

STEP 1: run census_list_variables.py, read the variable names it prints, and fix the
MEASURE names below if they differ. The names here are my best guess and are NOT verified.
"""
BASE_URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
COMM_LEVEL = "HS4"            # agreed 2 Nov 2026: start at HS4, rerun at HS6 later
START_MONTH = "2022-01"       # 2022 is used only for SeaShare
END_MONTH = "2024-12"         # stop before 2025 tariffs

# Names of the identifier columns in the API (verify)
COMMODITY_VAR = "I_COMMODITY"
COUNTRY_VAR = "CTY_CODE"
DISTRICT_VAR = "DISTRICT"
COMM_LEVEL_PARAM = "COMM_LVL"   # query parameter that selects HS2 / HS4 / HS6 / HS10 (verify)

# Measures (verify every one of these against the variables list)
MEASURES = {
    "charges": "CNT_CHA_MO",   # containerized vessel charges, freight and insurance, USD
    "weight": "CNT_WGT_MO",        # containerized vessel shipping weight, kg
    "cnt_value": "CNT_VAL_MO",     # containerized vessel import value, USD
    "gen_value": "GEN_VAL_MO",     # total general import value, USD (customs value)
}

# Origin countries to pull (Census country codes, verify). Use ["*"] for all countries,
# but that is very large. Start with Asian origins that matter for Suez exposure.
COUNTRIES = {
    "5700": "China", "5820": "Hong Kong", "5830": "Taiwan", "5800": "South Korea",
    "5880": "Japan", "5520": "Vietnam", "5490": "Thailand", "5570": "Malaysia",
    "5590": "Singapore", "5600": "Indonesia", "5683": "Philippines", "5330": "India",
    "5380": "Bangladesh", "5420": "Sri Lanka", "5350": "Pakistan",
}
RAW_DIR = "data/raw/census"
