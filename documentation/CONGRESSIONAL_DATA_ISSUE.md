# Congressional District Data Issue

## Problem Identified

The congressional district statewide data (`2018_2024_congressional_results_combined.csv`) contains **incorrect presidential/statewide results** for congressional districts.

### Example - Texas Congressional District 9 (2020 Presidential):

| Source | Biden % | Trump % | Winner |
|--------|---------|---------|--------|
| **Actual Results** (Texas Politics Project) | 75.7% | 23.2% | Biden +52.5 |
| **Our Parsed Data** (WRONG) | 46.7% | 52.0% | Trump +5.3 |

This is a **huge discrepancy** - we show Trump winning a district Biden won by 52 points!

## Root Cause

The PDFs we downloaded use **PLANC2308**, which is a 2020 Census redistricting plan created in 2025. This plan is being retroactively applied to analyze old elections using hypothetical "what if these districts existed" boundaries.

This does NOT match the **actual congressional districts** used in 2018-2024 elections:
- **2018 & 2020**: Used PLANC2100 (2011 redistricting)
- **2022 & 2024**: Used PLANC2193 (2021 redistricting after 2020 census)

## Impact

- ❌ **Congressional district vs_top_ticket analysis is INVALID**
- ❌ **Congressional crossover appeal analysis is INVALID**
- ❌ **Congressional recruitment scoring is INVALID**
- ✅ **Congressional race results** (actual U.S. House races) are CORRECT
- ✅ **State House district analysis** is CORRECT
- ✅ **State Senate district analysis** is CORRECT

## Current Status

The incorrect file has been renamed to:
```
texas_election_data/pdf_extracts/2018_2024_congressional_results_combined_INCORRECT_DO_NOT_USE.csv
```

The `MultiYearDistrictCandidateAnalyzer` now:
- ✅ Detects missing congressional statewide data
- ✅ Shows warning message on initialization
- ✅ Raises clear error if congressional vs_top_ticket analysis is attempted
- ✅ State House and Senate analysis continue to work normally

## Solutions

### Option 1: Download Correct PDF Reports (Recommended)

Download Red-206 reports for the ACTUAL district plans used:

**For 2018 & 2020 elections:**
- Plan: PLANC2100
- Files needed:
  - `PLANC2100r206_18G.pdf` (2018 General Election)
  - `PLANC2100r206_20G.pdf` (2020 General Election)
- Source: https://data.capitol.texas.gov/dataset/planc2100

**For 2022 & 2024 elections:**
- Plan: PLANC2193 (or check actual plan used)
- Files needed:
  - `PLANC2193r206_22G.pdf` (2022 General Election)
  - `PLANC2193r206_24G.pdf` (2024 General Election)
- Source: https://data.capitol.texas.gov/dataset/planc2193

Then update `parse_congressional_districts.py` to use these correct PDFs.

### Option 2: Use VTD Data with District Mapping

The VTD (Voter Tabulation District) datasets we already have contain precinct-level results that can be aggregated to congressional districts IF we have VTD-to-Congressional-District mapping files.

Requirements:
1. VTD-to-Congressional-District mapping for each redistricting period
2. Update aggregation script to use these mappings
3. Aggregate VTD data to congressional district level

### Option 3: Use Third-Party Verified Source

Use pre-aggregated data from reliable sources:
- **Daily Kos Elections**: Maintains presidential results by congressional district
  - 2020 data: https://www.dailykos.com/stories/2020/11/19/1163009/
  - Available in Google Sheets format
- **Texas Politics Project** (University of Texas): Cited in our verification
  - https://texaspolitics.utexas.edu/

## Next Steps

1. **Short term**: Congressional vs_top_ticket analysis remains disabled
2. **Medium term**: Implement Option 1 (download correct PDFs) or Option 3 (use Daily Kos data)
3. **Long term**: Add data validation checks to catch similar issues

## Files Affected

**Scripts that need updates:**
- `data_collection/parse_congressional_districts.py` - Update to use correct PDFs
- `data_collection/download_congressional_pdfs.py` - NEW script needed to download correct PDFs

**Analysis tools:**
- `analysis_tools/district_candidate_analyzer_multiyear.py` - ✅ Already updated to handle missing data

**Documentation:**
- `README.md` - Should note congressional analysis limitation
- `MULTIYEAR_ANALYSIS_WITH_COMPETITIVENESS.md` - Should note limitation

## References

- [Texas Politics Project - Congressional District Comparison](https://texaspolitics.utexas.edu/blog/comparing-trump-biden-vote-shares-old-and-new-texas-congressional-districts)
- [Texas Capitol Data Portal - PLANC2100](https://data.capitol.texas.gov/dataset/planc2100)
- [Texas Redistricting History](https://redistricting.capitol.texas.gov/history)
- [Daily Kos Elections - Presidential Results by District](https://www.dailykos.com/stories/2020/11/19/1163009/)

---

**Last Updated:** 2025-01-16
**Issue Discovered By:** User observation that TX-9 and TX-32 2020 results were backwards
