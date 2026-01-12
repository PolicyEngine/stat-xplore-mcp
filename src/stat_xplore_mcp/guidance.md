---
name: dwp-stat-xplore
description: Access DWP benefit and income statistics via the Stat-Xplore Open Data API. Use when fetching UK government data on Households Below Average Income (HBAI), Universal Credit, PIP, ESA, Housing Benefit, or other DWP benefits. Supports querying income distributions, poverty metrics, benefit caseloads, and demographic breakdowns programmatically.
user_invocable: true
---

# DWP Stat-Xplore Open Data API

## Quick Start

```python
import requests
import numpy as np

API_KEY = "your-api-key"
BASE_URL = "https://stat-xplore.dwp.gov.uk/webapi/rest/v1"
headers = {"APIKey": API_KEY, "Content-Type": "application/json"}

query = {
    "database": "str:database:HBAI",
    "measures": ["str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN"],
    "dimensions": [["str:field:HBAI:V_F_HBAI:YEAR"]]
}

response = requests.post(f"{BASE_URL}/table", headers=headers, json=query, timeout=30)
data = response.json()
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/schema` | GET | Discover databases, fields, measures |
| `/schema/{id}` | GET | Get details for specific object |
| `/table` | POST | Execute queries |
| `/rate_limit` | GET | Check quota (2,000 requests/hour) |

## Query Structure

```python
query = {
    "database": "str:database:HBAI",
    "measures": ["str:count:HBAI:V_F_HBAI"],
    "dimensions": [
        ["str:field:HBAI:V_F_HBAI:YEAR"],
        ["str:field:HBAI:V_F_HBAI:NEWFAMBU"]
    ],
    "recodes": {
        "str:field:HBAI:V_F_HBAI:YEAR": {
            "map": [["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2324"]],
            "total": True
        }
    }
}
```

## Response Parsing

```python
data = response.json()
years = [item["labels"][0] for item in data["fields"][0]["items"]]
groups = [item["labels"][0] for item in data["fields"][1]["items"]]
values = np.array(data["cubes"]["str:count:HBAI:V_F_HBAI"]["values"])
values = values.reshape(len(years), len(groups))
```

---

# HBAI Database Reference

Database ID: `str:database:HBAI`

## Measures

| Measure | ID |
|---------|-----|
| Population count | `str:count:HBAI:V_F_HBAI` |
| Median BHC (latest prices) | `str:statfn:HBAI:V_F_HBAI:S_OE_BHC:MEDIAN` |
| Median AHC (latest prices) | `str:statfn:HBAI:V_F_HBAI:S_OE_AHC:MEDIAN` |
| Median BHC (year prices/nominal) | `str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN` |
| Median AHC (year prices/nominal) | `str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN` |
| Mean BHC (latest prices) | `str:statfn:HBAI:V_F_HBAI:S_OE_BHC:MEAN` |
| Mean AHC (latest prices) | `str:statfn:HBAI:V_F_HBAI:S_OE_AHC:MEAN` |

Pattern: `str:statfn:HBAI:V_F_HBAI:{measure}:{MEDIAN|MEAN}`

## Verified Queryable Fields

Fields tested and confirmed working with median income queries:

| Field | ID | Values | Available From |
|-------|-----|--------|----------------|
| **YEAR** | `str:field:HBAI:V_F_HBAI:YEAR` | See year codes below | 1994/95 |
| **NEWFAMBU** | `str:field:HBAI:V_F_HBAI:NEWFAMBU` | Pensioner/Working-age family | 1994/95 |
| **ECOBU** | `str:field:HBAI:V_F_HBAI:ECOBU` | In work/Workless | 1996/97 |
| **DIS** | `str:field:HBAI:V_F_HBAI:DIS` | Disabled/Not disabled (individual) | 1995/96 |
| **NEWFAMBU_UC** | `str:field:HBAI:V_F_HBAI:NEWFAMBU_UC` | In UC family/Not in UC family | 2018/19 |
| **OQINAHC** | `str:field:HBAI:V_F_HBAI:OQINAHC` | Quintiles 1-5 (AHC) | 1994/95 |
| **TYPE_AGECAT** | `str:field:HBAI:V_F_HBAI:TYPE_AGECAT` | Child/Working-Age/Pensioner | 1994/95 |

### NEWFAMBU Values (Family Type)

```python
"str:value:HBAI:V_F_HBAI:NEWFAMBU:C_HBAI_NEWFAMBU_TYPE:1"  # Pensioner family
"str:value:HBAI:V_F_HBAI:NEWFAMBU:C_HBAI_NEWFAMBU_TYPE:2"  # Working-age family
```

### ECOBU Values (Economic Status)

```python
"str:value:HBAI:V_F_HBAI:ECOBU:C_HBAI_FAMECOBU:1"   # At least one adult in work
"str:value:HBAI:V_F_HBAI:ECOBU:C_HBAI_FAMECOBU:2"   # Workless family
"str:value:HBAI:V_F_HBAI:ECOBU:C_HBAI_FAMECOBU:-1"  # Not available (before 1996/97)
```

### DIS Values (Individual Disability)

```python
"str:value:HBAI:V_F_HBAI:DIS:C_HBAI_DIS:0"   # Not disabled
"str:value:HBAI:V_F_HBAI:DIS:C_HBAI_DIS:1"   # Disabled
"str:value:HBAI:V_F_HBAI:DIS:C_HBAI_DIS:-1"  # Not available (before 1995/96)
```

### NEWFAMBU_UC Values (UC Applicability)

```python
"str:value:HBAI:V_F_HBAI:NEWFAMBU_UC:C_HBAI_NEWFAMBU_UC:0"   # Not in UC applicable family
"str:value:HBAI:V_F_HBAI:NEWFAMBU_UC:C_HBAI_NEWFAMBU_UC:1"   # In UC applicable family
"str:value:HBAI:V_F_HBAI:NEWFAMBU_UC:C_HBAI_NEWFAMBU_UC:-1"  # Not available (before 2018/19)
```

### OQINAHC Values (Quintiles AHC)

```python
"str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:1"  # Bottom quintile
"str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:2"  # Second quintile
"str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:3"  # Third quintile
"str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:4"  # Fourth quintile
"str:value:HBAI:V_F_HBAI:OQINAHC:C_HBAI_OQINAHC:5"  # Top quintile
```

### TYPE_AGECAT Values

```python
"str:value:HBAI:V_F_HBAI:TYPE_AGECAT:C_HBAI_TYPE:1"  # Child
"str:value:HBAI:V_F_HBAI:TYPE_AGECAT:C_HBAI_TYPE:2"  # Working-Age
"str:value:HBAI:V_F_HBAI:TYPE_AGECAT:C_HBAI_TYPE:3"  # Pensioner
```

## Other Direct Fields (Schema-Verified)

These fields are available in the schema but may have query restrictions:

| Field | ID | Description |
|-------|-----|-------------|
| Age Band | `AGEBAND_CHLOW` | Age bands with child splits |
| Gender | `SEX` | Male/Female |
| Education | `EDATTAIN` | Educational attainment |
| Marital Status | `COUPLE` | Single/Cohabiting/Married |
| Savings | `CAPITAL` | Savings bands |
| Num Children | `NUMBKIDS` | 0/1/2/3+ children |
| Youngest Child | `YOUNGCH` | Age of youngest child |
| Region | `GVTREGN_LON` | UK regions (3-year avg required) |
| Tenure | `TENHBAI` | Owner/Social rent/Private rent |
| Council Tax | `CTBAND` | Bands A-H |
| Food Security | `HFS_STATUS` | High/Marginal/Low/Very low (2019/20+) |

## Fields in Groups (Not Directly Queryable)

These fields exist in the web UI but are inside GROUP containers and cannot be queried via API:

- Disability in Family (DISFAM)
- State Support/Benefits received (UC, HB, CTC, WTC, ESA, JSA, etc.)
- Low income thresholds (LOW60BHC, LOW60AHC, etc.)
- Material deprivation

**Workaround**: Use the web UI to build queries with these fields, then export as JSON.

## Year Codes

| Year | Code | Year | Code | Year | Code |
|------|------|------|------|------|------|
| 1994-95 | 9495 | 2004-05 | 405 | 2014-15 | 1415 |
| 1995-96 | 9596 | 2005-06 | 506 | 2015-16 | 1516 |
| 1996-97 | 9697 | 2006-07 | 607 | 2016-17 | 1617 |
| 1997-98 | 9798 | 2007-08 | 708 | 2017-18 | 1718 |
| 1998-99 | 9899 | 2008-09 | 809 | 2018-19 | 1819 |
| 1999-00 | 9900 | 2009-10 | 910 | 2019-20 | 1920 |
| 2000-01 | 1 | 2010-11 | 1011 | **2020-21** | **N/A** |
| 2001-02 | 102 | 2011-12 | 1112 | 2021-22 | 2122 |
| 2002-03 | 203 | 2012-13 | 1213 | 2022-23 | 2223 |
| 2003-04 | 304 | 2013-14 | 1314 | 2023-24 | 2324 |

**Note**: 2020-21 unavailable due to COVID-19.

---

# Working Examples

## Median Income by Family Type and Economic Status

```python
query = {
    "database": "str:database:HBAI",
    "measures": [
        "str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN",
        "str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN"
    ],
    "dimensions": [
        ["str:field:HBAI:V_F_HBAI:YEAR"],
        ["str:field:HBAI:V_F_HBAI:NEWFAMBU"],
        ["str:field:HBAI:V_F_HBAI:ECOBU"]
    ],
    "recodes": {
        "str:field:HBAI:V_F_HBAI:YEAR": {
            "map": [["str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:2324"]]
        }
    }
}
```

Returns median income for:
- Pensioner family × In work / Workless
- Working-age family × In work / Workless

## Historic Series with Quintiles

```python
year_codes = ["9495", "9596", "9697", "9798", "9899", "9900",
              "1", "102", "203", "304", "405", "506", "607", "708", "809", "910",
              "1011", "1112", "1213", "1314", "1415", "1516", "1617", "1718",
              "1819", "1920", "2122", "2223", "2324"]

query = {
    "database": "str:database:HBAI",
    "measures": [
        "str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN",
        "str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN"
    ],
    "dimensions": [
        ["str:field:HBAI:V_F_HBAI:YEAR"],
        ["str:field:HBAI:V_F_HBAI:OQINAHC"],
        ["str:field:HBAI:V_F_HBAI:NEWFAMBU"]
    ],
    "recodes": {
        "str:field:HBAI:V_F_HBAI:NEWFAMBU": {
            "map": [
                ["str:value:HBAI:V_F_HBAI:NEWFAMBU:C_HBAI_NEWFAMBU_TYPE:2"],
                ["str:value:HBAI:V_F_HBAI:NEWFAMBU:C_HBAI_NEWFAMBU_TYPE:1"]
            ],
            "total": True
        },
        "str:field:HBAI:V_F_HBAI:YEAR": {
            "map": [[f"str:value:HBAI:V_F_HBAI:YEAR:C_HBAI_YEAR:{code}"] for code in year_codes]
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
    }
}
```

## Parsing Multi-Dimensional Results

```python
import numpy as np
import pandas as pd

response = requests.post(f"{BASE_URL}/table", headers=headers, json=query, timeout=30)
data = response.json()

years = [item["labels"][0] for item in data["fields"][0]["items"]]
quintiles = [item["labels"][0] for item in data["fields"][1]["items"]]
family_types = [item["labels"][0] for item in data["fields"][2]["items"]]

n_years, n_quintiles, n_types = len(years), len(quintiles), len(family_types)

bhc = np.array(data["cubes"]["str:statfn:HBAI:V_F_HBAI:S_OE_BHC_INYR:MEDIAN"]["values"])
bhc = bhc.reshape(n_years, n_quintiles, n_types)

ahc = np.array(data["cubes"]["str:statfn:HBAI:V_F_HBAI:S_OE_AHC_INYR:MEDIAN"]["values"])
ahc = ahc.reshape(n_years, n_quintiles, n_types)

rows = []
for i, year in enumerate(years):
    for j, quintile in enumerate(quintiles):
        for k, family_type in enumerate(family_types):
            rows.append({
                "year": year,
                "quintile": quintile,
                "family_type": family_type,
                "median_bhc": bhc[i, j, k],
                "median_ahc": ahc[i, j, k]
            })

df = pd.DataFrame(rows)
```

---

# Important Notes

## Income Definitions

- **BHC**: Before Housing Costs (rent/mortgage not deducted)
- **AHC**: After Housing Costs (housing costs deducted)
- **Equivalised**: Adjusted for household size
- **SPI-adjusted**: Top incomes corrected for under-reporting
- **Year prices**: Nominal (not inflation-adjusted)
- **Latest prices**: Real (CPI-adjusted to latest year)

## Data Limitations

- **DIS field**: Individual-level disability, not household-level
- **NEWFAMBU_UC**: Only available from 2018/19
- **ECOBU**: Only available from 1996/97
- **Regional/Ethnicity**: Require 3-year averaging due to sample size
- **2020-21**: No data due to COVID-19

---

# Other Databases

| Database | ID |
|----------|-----|
| Universal Credit (People) | `str:database:UC_Monthly` |
| Universal Credit (Households) | `str:database:UC_Households` |
| PIP | `str:database:PIP_Monthly` |
| ESA | `str:database:ESA_Caseload` |
| Housing Benefit | `str:database:hb_new` |
| State Pension | `str:database:SP` |
| Children in Low Income | `str:database:CILIF_ABS` |