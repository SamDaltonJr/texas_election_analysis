# Texas Capitol Data Portal - PDF Election Results

## Overview

The Texas Capitol Data Portal contains comprehensive election results PDFs with **statewide race results broken down by legislative districts**. These are excellent sources for your analysis.

## ✅ Successfully Extracted: 2018 General Election

### File: 2018 State House District Results
- **URL:** https://data.capitol.texas.gov/dataset/71af633c-21bf-42cf-ad48-4fe95593a897/resource/4391b9ea-7e1b-4872-acb4-799cb2a3d498/download/planh2316r206_18g.pdf
- **Plan:** PLANH2316
- **Districts:** All 150 Texas State House Districts + Statewide totals
- **Races Included:**
  - U.S. Senate (Cruz vs. O'Rourke vs. Dikeman)
  - Governor (Abbott vs. Valdez vs. Tippetts)
  - Lieutenant Governor (Patrick vs. Collier vs. McKennon)
  - Attorney General (Paxton vs. Nelson vs. Sanders + others)
- **Data Format:** Vote counts and percentages for each candidate in each district
- **Extracted File:** `texas_election_data/pdf_extracts/2018_house_district_results_clean.csv`
- **Records:** 1,510 (151 districts × ~10 candidates)
- **Status:** ✅ **Successfully parsed and ready for analysis!**

### Sample Data Structure:
```csv
year,district,office,candidate,party,votes,percentage
2018,STATE,U.S. Senate,Cruz,REP,4259630,50.9
2018,STATE,U.S. Senate,O'Rourke,DEM,4044073,48.3
2018,1,U.S. Senate,Cruz,REP,47345,74.4
2018,1,U.S. Senate,O'Rourke,DEM,15929,25.0
```

---

## 📋 Available PDFs for Other Years

### State House District Results

Based on the naming pattern `planh####r206_##g.pdf`, similar files should exist for:

**2020 General Election:**
- Search for: `planh####r206_20g.pdf` or similar patterns
- Expected data: Presidential, U.S. Senate, State races by House district

**2022 General Election:**
- Search for: `planh####r206_22g.pdf` or similar patterns
- Expected data: Governor, U.S. Senate (if applicable), State races by House district

**2024 General Election:**
- Search for: `planh####r206_24g.pdf` or similar patterns
- Expected data: Presidential, U.S. Senate, State races by House district

### Congressional District Results

**2024 General Election - Congressional Districts:**
- **URL:** https://data.capitol.texas.gov/dataset/6c8aed8d-c0e7-4520-b917-b10dcee44f67/resource/db73dee1-0b2d-4029-ad92-3bffb4bc0265/download/planc2308_r206_election24g.pdf
- **Plan:** PLANC2308
- **Districts:** All 38 Texas Congressional Districts
- **Contains:** Voter registration, turnout by Congressional district
- **Downloaded:** `texas_election_data/pdf_extracts/2024_sample.pdf`

---

## 🔍 How to Find More PDFs

### Method 1: Direct Search on Portal
Visit: https://data.capitol.texas.gov/topic/elections

Use the search function with these keywords:
- "election analysis"
- "r206" (Report 206 - Election Analysis)
- "general election"
- Year (2020, 2022, 2024)

### Method 2: URL Pattern Matching
The URLs follow this pattern:
```
https://data.capitol.texas.gov/dataset/{DATASET_ID}/resource/{RESOURCE_ID}/download/{FILENAME}.pdf
```

Common filename patterns:
- State House: `planh####r206_YYg.pdf` (YY = year, e.g., 18, 20, 22, 24)
- Congressional: `planc####r206_election##g.pdf`
- State Senate: `plans####r206_##g.pdf` (if available)

### Method 3: Browse Datasets
1. Go to https://data.capitol.texas.gov/dataset
2. Filter by:
   - Tags: "elections", "red-206", "election analysis"
   - Organization: "Texas Legislative Council"
3. Look for datasets with "Election Analysis" or "Red-206" in the title

---

## 📊 What These PDFs Contain

### Typical Structure:
1. **Voter Registration & Turnout** (first few pages)
   - Total registered voters by district
   - SSVR-T (Spanish Surname Voter Registration %)
   - Total turnout
   - Turnout rate (TO/VR)

2. **Race Results** (main section)
   - Statewide race results broken down by each district
   - Multiple candidates per race
   - Vote counts and percentages
   - All statewide offices included

3. **Format:**
   - Tables with districts as rows
   - Candidate votes/percentages as columns
   - STATE row for statewide totals

---

## 🛠️ Tools Created

### 1. PDF Extraction Script
**File:** `extract_pdf_election_data.py`
- Downloads PDFs from URLs
- Extracts text and tables using pdfplumber
- Saves raw extraction for review
- **Usage:** Add PDF URLs to the script and run

### 2. Parser Script
**File:** `parse_house_district_results_v2.py`
- Parses extracted tables into structured data
- Handles multiple races and candidates
- Outputs clean CSV files
- **Usage:** Run after extracting PDF

### 3. Quick Parser Command
For future PDFs, use this workflow:
```python
# 1. Download PDF
import requests
r = requests.get('PDF_URL')
open('filename.pdf', 'wb').write(r.content)

# 2. Extract with pdfplumber
import pdfplumber
pdf = pdfplumber.open('filename.pdf')
# ... extract tables ...

# 3. Parse and clean
# Use parse_house_district_results_v2.py as template
```

---

## 📈 Data Quality & Notes

### Strengths:
- ✅ Official source (Texas Legislative Council)
- ✅ Comprehensive coverage (all districts)
- ✅ Includes statewide totals for verification
- ✅ Consistent format across years
- ✅ Multiple statewide races in one file

### Limitations:
- ⚠️ PDFs may vary slightly in format between years
- ⚠️ Parser may need adjustment for different years
- ⚠️ Data may differ slightly from official TX SOS results (noted in PDFs)
- ⚠️ Some pages have continuation/duplicate data (need deduplication)

### Verification:
Compare against official results from:
- Texas Secretary of State: https://www.sos.state.tx.us/elections/historical/
- Statewide totals in the "STATE" row should match official totals

---

## 🎯 Next Steps

### To Get 2020, 2022, 2024 State House District Data:

1. **Search the Portal:**
   - Visit: https://data.capitol.texas.gov/topic/elections
   - Search: "Red-206 election 2020", "Red-206 election 2022", "Red-206 election 2024"
   - Look for "HOUSE DISTRICTS" PDFs

2. **Try Common Patterns:**
   ```
   planh2316r206_20g.pdf  (2020)
   planh2316r206_22g.pdf  (2022)
   planh2316r206_24g.pdf  (2024)
   ```

3. **Contact Portal:**
   If not found, you can request the data:
   - Email: data@capitol.texas.gov
   - Request: "Election Analysis Report Red-206 for State House Districts, 2020/2022/2024 General Elections"

4. **Alternative:**
   Check if they have updated plan numbers:
   - Plans change after redistricting (2021 redistricting may have changed plan numbers)
   - Look for newer plan numbers like PLANH2XXX

---

## 📂 File Organization

```
texas_election_data/
├── pdf_extracts/
│   ├── texas_election_2018.pdf          # Original PDF
│   ├── raw_extract_2018.txt             # Extracted text/tables
│   ├── 2018_house_district_results.csv  # Parsed data (with duplicates)
│   ├── 2018_house_district_results_clean.csv  # ✅ Clean, deduplicated data
│   └── 2024_sample.pdf                  # Congressional district sample
```

---

## ✅ Current Status Summary

| Year | Type | Races | Status | File |
|------|------|-------|--------|------|
| 2018 | State House | Senate, Governor, Lt. Gov, AG | ✅ Complete | `2018_house_district_results_clean.csv` |
| 2020 | State House | Presidential, Senate?, State | 🔍 Need to find PDF | - |
| 2022 | State House | Governor, State | 🔍 Need to find PDF | - |
| 2024 | State House | Presidential, Senate, State | 🔍 Need to find PDF | - |
| 2024 | Congressional | Registration/Turnout | ✅ PDF Downloaded | `2024_sample.pdf` |

---

## 🔗 Key Resources

- **Texas Capitol Data Portal:** https://data.capitol.texas.gov/topic/elections
- **TX Legislative Council:** The agency that produces these reports
- **Red-206 Reports:** "Election Analysis" series
- **Original 2018 PDF:** [Direct Link](https://data.capitol.texas.gov/dataset/71af633c-21bf-42cf-ad48-4fe95593a897/resource/4391b9ea-7e1b-4872-acb4-799cb2a3d498/download/planh2316r206_18g.pdf)

---

**Great find!** This PDF data source gives you exactly what you need: **statewide race results broken down by State House districts**, which is perfect for your election analysis model!
