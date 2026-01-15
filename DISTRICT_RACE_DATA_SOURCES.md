# Texas District-Level Race Data Sources

## Summary
This document describes where to find **actual district race results** (State House, State Senate, and U.S. Congressional races) as opposed to statewide races broken down by district.

---

## Key Finding: Red-226 District Election Reports

### Report Type: Red-226 "District Election Report"
**Primary Source for 2024 District Races**

### URL Pattern (wrm.capitol.texas.gov):
```
House Districts (1-150):
https://wrm.capitol.texas.gov/fyiwebdocs/PDF/house/dist{N}/r8.pdf

State Senate Districts (1-31):
https://wrm.capitol.texas.gov/fyiwebdocs/PDF/senate/dist{N}/r8.pdf

Congressional Districts (1-38):
https://wrm.capitol.texas.gov/fyiwebdocs/PDF/congress/dist{N}/r8.pdf
```

### What These Reports Contain:

**State House Reports (r8.pdf):**
- 2024 General Election data
- Geographic Plan: PLANH2316
- Census Data: 2020 Census
- Last Updated: February 25, 2025
- **Shows actual State Rep race for that district** (e.g., Lambert vs Goolsbee for HD-71)
- Also includes: President, U.S. Senate, U.S. Representative, Railroad Commissioner, Supreme Court, CCA, SBOE, State Senate (where applicable)
- Voter registration and turnout statistics
- District totals vs. statewide totals with percentages

**State Senate Reports (r8.pdf):**
- 2024 General Election data
- Geographic Plan: PLANS2168
- Census Data: 2020 Census
- Last Updated: February 25, 2025
- **Shows actual State Senate race for that district** (when contested)
- Also includes: President, U.S. Senate, U.S. Representative (multiple districts), Railroad Commissioner, Supreme Court, CCA, SBOE, State Representative races (multiple districts within the senate district)
- Voter registration and turnout statistics

**Congressional District Reports (r8.pdf):**
- **2016 General Election data** (NOT 2024 - these are outdated!)
- Geographic Plan: PLANC235
- Census Data: 2010 Census
- Last Updated: February 9, 2017
- **Shows actual U.S. Representative race for that district**
- Also includes: President, Railroad Commissioner, Supreme Court, CCA, SBOE, State Senate, State Representative races
- NOTE: Congressional r8 reports have NOT been updated for recent elections

### Example Reports Examined:

**House District 71 (r8.pdf):**
- State Rep 71: Goolsbee (D) 13,678 (19.0%) vs Lambert (R) 58,413 (81.0%)
- Also shows U.S. Rep 19 and U.S. Rep 25 (portions of HD-71 in different Congressional districts)
- Shows State Sen 10: King (R) 89.9% vs Morris (D) 10.1%

**Senate District 1 (r8.pdf):**
- Shows parts of multiple U.S. Rep districts (1, 4, 5)
- Shows multiple State Rep races (1, 2, 5, 6, 7, 11, 62)
- State Sen 1 race would appear at top if contested (in 2024, no opponent listed means unopposed or data structure different)

**Congressional District 1 (r8.pdf) - OUTDATED:**
- 2016 data only
- U.S. Rep 1: Gohmert (R) 73.9% vs McKellar (D) 24.1% vs Gray (L) 1.9%
- State Sen 1: Hughes (R) 100.0% (unopposed)
- Multiple State Rep races shown

---

## Historical Election Years - Other Report Types

### 2018, 2020, 2022 Congressional District Races:
**Status:** r8.pdf files for Congressional districts have NOT been updated past 2016.

**Alternative:** Must use Capitol Data Portal or other sources for recent Congressional race data.

### Other Report Numbers Found:
In the `/congress/dist1/` directory:
- r4.pdf (Last Modified: January 13, 2015)
- r5.pdf (Last Modified: January 11, 2019) - Red-160 Demographic Report, NOT election results
- r6.pdf (Last Modified: January 13, 2015)
- r7.pdf (Last Modified: February 9, 2017)
- r8.pdf (Last Modified: February 9, 2017) - Red-226 Election Report
- r9.pdf (Last Modified: January 13, 2015)

---

## Capitol Data Portal (data.capitol.texas.gov)

### URL: https://data.capitol.texas.gov/topic/elections

### Available Datasets:

#### 2024 Election Data:
- **Individual District Pages** available via API
  - 2024 General - State Representative District {N}
  - 2024 General - State Senator District {N}
  - 2024 General - U.S. Representative District {N}
  - Example: https://data.capitol.texas.gov/dataset/2024_general/resource/{resource_id}
  - API Endpoint format: https://ted.capitol.texas.gov/api/Offices/{office_id}/{district_id}/vtd

- **Comprehensive VTD Data** (CSV format, zipped)
  - 2024 General VTDs Election Data (Coverage: 2012-2024)
  - Includes all available election data by VTD
  - URL: https://data.capitol.texas.gov/dataset/comprehensive-election-datasets-compressed-format

- **Special Election Datasets**
  - 2024 Senate Dist 15
  - 2024 House District 56
  - 2024 House Dist 2 2nd
  - 2024 Congress Dist 18
  - 2023 House District 2
  - 2022 House District 147
  - 2022 Congress Dist 34

#### 2022 Election Data:
- **Individual District Pages** available via API
  - 2022 General - State Representative District {N}
  - 2022 General - U.S. Representative District {N}
  - Example: https://data.capitol.texas.gov/dataset/2022_general/resource/{resource_id}

- **Comprehensive VTD Data** (CSV format, zipped)
  - 2022 General VTDs Election Data (Coverage: 2012-2022)
  - 2022 Primary VTDs Election Data (Coverage: 2012-2022)

- **Primary Elections**
  - 2022 Republican Primary - State Representative District {N}
  - 2022 Democratic Primary - State Representative District {N}

#### 2020 Election Data:
- **Individual District Pages** available via API
  - 2020 General - State Representative District {N}
  - Example: https://data.capitol.texas.gov/dataset/2020_general/resource/{resource_id}

- **Comprehensive VTD Data** (CSV format, zipped)
  - 2020 General VTDs Election Data (Coverage: 2012-2020)

- **Archived Data**
  - 2010s Archived Election Data - 2020 General VTD Election Data
  - URL: https://data.capitol.texas.gov/dataset/aab5e1e5-d585-4542-9ae8-1108f45fce5b

#### 2018 Election Data:
- **Election Analysis PDFs** (Red-206 format)
  - Shows statewide races broken down BY district (not district races themselves)
  - URL: https://data.capitol.texas.gov/dataset/6c8aed8d-c0e7-4520-b917-b10dcee44f67/resource/6cce2134-c911-4bdf-97fe-a44ad4a14b17/download/planc2308_r206_election18g.pdf

- **Note:** Individual State House/Senate district race datasets for 2018 are not readily visible on the portal's main pages

### Data Portal Features:
- **VTD (Voter Tabulation District) Level Data**: All datasets report results by VTD
- **API Access**: Programmatic access via ted.capitol.texas.gov API
- **GIS Integration**: Shapefiles available for mapping
- **Precinct Crosswalks**: Excel files relating precincts to districts
  - Precincts24G_Districts.xlsx (2024 General)
  - Precincts22G_Districts.xlsx (2022 General)
  - Precincts20G_Districts.xlsx (2020 General)

---

## Geographic Plans Used

### State House:
- **PLANH2316** (2024 elections) - Created 10/13/2021, 2020 Census

### State Senate:
- **PLANS2168** (2024 elections) - Created 10/04/2021, 2020 Census

### Congressional:
- **PLANC2308** (2024 elections) - Current plan
- **PLANC235** (2016 elections shown in r8.pdf) - Created 02/27/2012, 2010 Census

---

## Report Type Naming Conventions

### Texas Legislative Council Report Types:
- **Red-206**: Election Analysis (statewide races broken down BY district)
- **Red-226**: District Election Report (actual district races + other races within that district)
- **Red-160**: District Population Analysis with School District Subtotals (demographics, not elections)
- **Red-202**: District demographic/voter registration reports
- **Red-375**: Precinct lists by district

### File Naming Pattern:
```
Format: plan{CODE}_r{REPORT}_{ELECTION}.pdf

Examples:
- planc2308_r206_election24g.pdf (Red-206, Congressional, 2024 General)
- planc2308_r206_election22g.pdf (Red-206, Congressional, 2022 General)
- planc2308_r206_election20g.pdf (Red-206, Congressional, 2020 General)
- planc2308_r206_election18g.pdf (Red-206, Congressional, 2018 General)
- planh2316_r202_18g-20g.pdf (Red-202, House, 2018-2020 General comparison)
```

---

## Data Collection Strategy

### For 2024 District Races:

**State House (150 districts):**
```bash
for i in {1..150}; do
  curl -s "https://wrm.capitol.texas.gov/fyiwebdocs/PDF/house/dist${i}/r8.pdf" \
    -o "house_dist_${i}_2024.pdf"
done
```

**State Senate (31 districts):**
```bash
for i in {1..31}; do
  curl -s "https://wrm.capitol.texas.gov/fyiwebdocs/PDF/senate/dist${i}/r8.pdf" \
    -o "senate_dist_${i}_2024.pdf"
done
```

**Congressional (38 districts):**
- r8.pdf files are OUTDATED (2016 data)
- Use Capitol Data Portal API or comprehensive VTD datasets instead
- Individual district API: https://ted.capitol.texas.gov/api/Offices/{office_id}/{district_id}/vtd

### For 2018, 2020, 2022 District Races:

**Capitol Data Portal - Comprehensive VTD Datasets:**
1. Download comprehensive ZIP files:
   - 2024 General VTDs (contains 2012-2024)
   - 2022 General VTDs (contains 2012-2022)
   - 2020 General VTDs (contains 2012-2020)

2. Extract CSV files for specific races and years

3. Parse VTD-level data and aggregate to district level

**Capitol Data Portal - Individual District API:**
- Access via: https://ted.capitol.texas.gov/api/Offices/{office_id}/{district_id}/vtd
- Requires knowing office_id and district_id mappings
- Returns VTD-level JSON data

---

## Key Limitations & Notes

1. **Congressional District r8.pdf files are OUTDATED**
   - Only show 2016 election data
   - Have not been updated for 2018, 2020, 2022, or 2024
   - Use Capitol Data Portal for recent Congressional race data

2. **Red-226 vs Red-206 Distinction**
   - Red-226: Shows actual district races (what we want)
   - Red-206: Shows statewide races broken down BY district (what we already have)

3. **Data Freshness**
   - House/Senate r8.pdf: Updated February 25, 2025 (2024 election)
   - Congress r8.pdf: Last updated February 9, 2017 (2016 election)

4. **Multiple Data Sources Required**
   - 2024: Use r8.pdf for House/Senate, Capitol Data Portal for Congressional
   - 2022: Use Capitol Data Portal (VTD datasets or API)
   - 2020: Use Capitol Data Portal (VTD datasets or API)
   - 2018: Use Capitol Data Portal (VTD datasets or API)

5. **Data Format Differences**
   - wrm.capitol.texas.gov: PDF reports (easy to read, harder to parse)
   - data.capitol.texas.gov: CSV/JSON via API (harder to discover, easier to parse)

---

## Sources

- [Texas Legislative Council - Data](https://tlc.texas.gov/data)
- [Capitol Data Portal - Elections Topic](https://data.capitol.texas.gov/topic/elections)
- [Capitol Data Portal - Comprehensive Election Datasets](https://data.capitol.texas.gov/dataset/comprehensive-election-datasets-compressed-format)
- [Texas Secretary of State - Elections Results Archive](https://www.sos.state.tx.us/elections/historical/elections-results-archive.shtml)
- [House District Election Reports](https://wrm.capitol.texas.gov/fyiwebdocs/PDF/house/)
- [Senate District Election Reports](https://wrm.capitol.texas.gov/fyiwebdocs/PDF/senate/)
- [Congressional District Election Reports](https://wrm.capitol.texas.gov/fyiwebdocs/PDF/congress/)

---

## Next Steps

1. **Download all 2024 Red-226 reports** (House and Senate r8.pdf files)
2. **Extract 2024 Congressional race data** from Capitol Data Portal
3. **Download comprehensive VTD datasets** for 2018, 2020, 2022
4. **Build parser** for Red-226 PDF format
5. **Build parser** for Capitol Data Portal CSV/JSON format
6. **Consolidate into unified database** with standardized schema
