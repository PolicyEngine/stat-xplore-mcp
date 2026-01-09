name: dwp-stat-xplore description: Access DWP benefit and income statistics via the Stat-Xplore Open Data API. Use when fetching UK government data on Households Below Average Income (HBAI), Universal Credit, PIP, ESA, Housing Benefit, Attendance Allowance, or other DWP benefits. Supports querying income distributions, poverty metrics, benefit caseloads, and demographic breakdowns programmatically. license: Public API - requires free registration for API key
DWP Stat-Xplore Open Data API
Overview
Stat-Xplore is DWP's Open Data API providing access to UK benefit and income statistics. The REST API returns JSON and supports tabulation queries equivalent to creating tables in the web interface.
Base URL: https://stat-xplore.dwp.gov.uk/webapi/rest/v1
Rate Limit: 2,000 requests per hour per API key
Authentication
Obtain an API key from Stat-Xplore → Account → Open Data API Access.
headers = {
    "APIKey": "your-api-key",
    "Content-Type": "application/json"
}
API Endpoints
   Endpoint Method Purpose     /schema GET Discover available datasets, fields, and measures   /table POST Execute queries and retrieve data   /info GET Server configuration (languages)   /rate_limit GET Check remaining API quota   Schema Discovery
Navigate the schema hierarchy to find database IDs, field IDs, and measure IDs needed for queries.
import requests

BASE_URL = "https://stat-xplore.dwp.gov.uk/webapi/rest/v1"

# Get root folders
response = requests.get(f"{BASE_URL}/schema", headers=headers)
folders = response.json()["children"]

# Explore a specific database (e.g., HBAI)
response = requests.get(f"{BASE_URL}/schema/str:database:HBAI", headers=headers)
database_schema = response.json()
Key HBAI Database Identifiers
Database: str:database:HBAI
Common Measures (income medians):
str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN - Median income BHC (Before Housing Costs)
str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN - Median income AHC (After Housing Costs)
str:count:HBAI:V_F_HBAI - Population count
Common Fields:
str:field:HBAI:V_F_HBAI:YEAR - Financial year
str:field:HBAI:V_F_HBAI:NEWFAMBU - Type of individual (child/working-age/pensioner)
str:field:HBAI:V_F_HBAI:OQINAHC - Income quintile (AHC)
str:field:HBAI:V_F_HBAI:DQINBHC - Income decile (BHC)
Table Query Structure
POST to /table with JSON body containing:
query = {
    "database": "str:database:HBAI",  # Required: target database
    "measures": [                      # Required: what to calculate
        "str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN"
    ],
    "dimensions": [                    # Required: table axes (each inner list is one axis)
        ["str:field:HBAI:V_F_HBAI:YEAR"],
        ["str:field:HBAI:V_F_HBAI:NEWFAMBU"]
    ],
    "recodes": {                       # Optional: filter/group field values
        "str:field:HBAI:V_F_HBAI:YEAR": {
            "map": [
                ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2223"],
                ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2324"]
            ],
            "total": True  # Include total row
        }
    }
}
Recodes Explained
Recodes control which field values appear and how they're grouped:
"recodes": {
    "str:field:DATABASE:FIELD": {
        "map": [
            ["value1"],           # Single value
            ["value2", "value3"]  # Combined into one cell
        ],
        "total": True  # Add total row/column
    }
}
Omit a field from recodes → all values returned
Include only "total": True → get totals for all values
Complete HBAI Example
import requests
import numpy as np
import pandas as pd

API_KEY = "your-api-key"
BASE_URL = "https://stat-xplore.dwp.gov.uk/webapi/rest/v1"
headers = {"APIKey": API_KEY, "Content-Type": "application/json"}

# Query median income by year and quintile
query = {
    "database": "str:database:HBAI",
    "measures": [
        "str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN",
        "str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN"
    ],
    "recodes": {
        "str:field:HBAI:V_F_HBAI:NEWFAMBU": {
            "map": [
                ["str:value:HBAI:V_F_HBAI:NEWFAMBU:C_HBAI_NEWFAMBU_TYPE:2"],  # Working-age
                ["str:value:HBAI:V_F_HBAI:NEWFAMBU:C_HBAI_NEWFAMBU_TYPE:1"]   # Pensioner
            ],
            "total": True
        },
        "str:field:HBAI:V_F_HBAI:YEAR": {
            "map": [
                ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2122"],
                ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2223"],
                ["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2324"]
            ],
            "total": False
        },
        "str:field:HBAI:V_F_HBAI:OQINAHC": {
            "map": [
                ["str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:1"],
                ["str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:2"],
                ["str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:3"],
                ["str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:4"],
                ["str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:5"]
            ],
            "total": True
        }
    },
    "dimensions": [
        ["str:field:HBAI:V_F_HBAI:YEAR"],
        ["str:field:HBAI:V_F_HBAI:OQINAHC"],
        ["str:field:HBAI:V_F_HBAI:NEWFAMBU"]
    ]
}

response = requests.post(f"{BASE_URL}/table", headers=headers, json=query, timeout=30)
response.raise_for_status()
data = response.json()

# Parse response
years = [item["labels"][0] for item in data["fields"][0]["items"]]
quintiles = [item["labels"][0] for item in data["fields"][1]["items"]]
age_groups = [item["labels"][0] for item in data["fields"][2]["items"]]

# Extract values (flattened array, reshape based on dimensions)
bhc_values = np.array(
    data["cubes"]["str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN"]["values"]
).reshape(len(years), len(quintiles), len(age_groups))

ahc_values = np.array(
    data["cubes"]["str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN"]["values"]
).reshape(len(years), len(quintiles), len(age_groups))
Response Structure
{
    "query": {...},  # Echo of submitted query with full recodes
    "database": {"id": "...", "annotationKeys": [...]},
    "fields": [
        {
            "uri": "str:field:...",
            "label": "Financial Year",
            "items": [
                {"type": "RecodeItem", "labels": ["2023-24"], "uris": [...]}
            ]
        }
    ],
    "measures": [{"uri": "...", "label": "Median BHC Income"}],
    "cubes": {
        "str:statfn:...": {
            "values": [...]  # Flattened array - reshape by dimension sizes
        }
    },
    "annotationMap": {...}  # Footnotes and data quality notes
}
HBAI Year Codes Reference
   Year Code     1994-95 9495   1995-96 9596   ... ...   1999-00 9900   2000-01 1   2001-02 102   2002-03 203   ... ...   2021-22 2122   2022-23 2223   2023-24 2324   Note: 2020-21 data unavailable due to COVID-19 data quality issues.
HBAI Data Notes
Rounding Requirements
When publishing HBAI estimates:
Percentages: nearest whole percent
Numbers: nearest 0.1 million (100,000)
Amounts: nearest £1 (weekly), £100 (annual)
Three-Year Averages
Regional, country, and ethnicity estimates must use three-year averages:
three_year_avg = (year1 + year2 + year3) / 3
Income Definitions
BHC (Before Housing Costs): Housing costs not deducted
AHC (After Housing Costs): Housing costs deducted
Equivalised: Adjusted for household size/composition
SPI-adjusted: Corrected for top income under-reporting
Utility Functions
Check Rate Limit
def check_rate_limit(api_key):
    response = requests.get(
        f"{BASE_URL}/rate_limit",
        headers={"APIKey": api_key}
    )
    data = response.json()
    print(f"Remaining: {data['remaining']}/{data['limit']}")
    return data
Parse Financial Year to Date
def parse_fy_to_date(fy_label: str) -> pd.Timestamp | None:
    """Convert '2023-24' to April 1, 2023."""
    if fy_label == "Total":
        return None
    year_str = fy_label.split("-")[0]
    year = int(year_str) if len(year_str) == 4 else int(f"20{year_str}")
    return pd.Timestamp(year=year, month=4, day=1)
Other Available Databases
   Database ID     Universal Credit (People) str:database:UC_Monthly   Universal Credit (Households) str:database:UC_Households   PIP str:database:PIP_Monthly   ESA str:database:ESA_Caseload   Housing Benefit str:database:hb_new   Attendance Allowance str:database:AA   State Pension str:database:SP   Children in Low Income Families str:database:CILIF_ABS   Use schema discovery to explore fields and measures for each database.
Error Handling
try:
    response = requests.post(f"{BASE_URL}/table", headers=headers, json=query, timeout=30)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if response.status_code == 429:
        print("Rate limit exceeded - wait for reset")
    elif response.status_code == 400:
        print(f"Invalid query: {response.text}")
    elif response.status_code == 401:
        print("Invalid API key")
    raise
Generating Query JSON from Web UI
For complex queries, use the Stat-Xplore web interface:
Build your table visually
Click Download Table → "Open Data API Query (.json)"
Use the downloaded JSON as your query body