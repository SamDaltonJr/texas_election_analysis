# How to Get 2020-2024 Election Data

The automated scraper (`scrape_recent_elections.py`) couldn't download 2020-2024 data because the Texas election results website requires JavaScript. Here are your options:

---

## ✅ Option 1: MIT Election Lab (Easiest - County Level)

### Presidential 2020 ✅
You already have this! It's in: `dataverse_president_county_2000_2020_texas.csv`

### U.S. Senate 2020, 2024
1. Visit: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PEJ5QU
2. Download: "1976-2024-senate.csv"
3. Filter to Texas and 2020/2024
4. Save to: `texas_election_data/clean/`

### U.S. House 2020, 2022, 2024
1. Visit: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IG0UN2
2. Download: "1976-2024-house.csv"
3. Filter to Texas and 2020/2022/2024
4. Save to: `texas_election_data/clean/`

**Pros:** Clean, standardized data. Easy to use.
**Cons:** County-level only (no precinct detail). May not have all races.

---

## ✅ Option 2: OpenElections Project (Best for Precinct Data)

### Check GitHub Repository
1. Visit: https://github.com/openelections/openelections-data-tx
2. Look for files like:
   - `2020__tx__general__precinct.csv`
   - `2022__tx__general__precinct.csv`
   - `2024__tx__general__precinct.csv`
3. Download to: `texas_election_data/clean/`

**Pros:** Precinct-level detail. Well-cleaned. Consistent format.
**Cons:** May not have 2022/2024 yet (volunteer project).

---

## ✅ Option 3: Texas SOS Manual Download (Most Complete)

### For Each Year (2020, 2022, 2024):

1. **Go to Historical Elections Page**
   - 2024: https://www.sos.state.tx.us/elections/historical/2024.shtml
   - 2022: https://www.sos.state.tx.us/elections/historical/2022.shtml
   - 2020: https://www.sos.state.tx.us/elections/historical/2020.shtml

2. **Look for Download Links**
   Search the page for:
   - "Canvass" (official certified results)
   - "County-level returns"
   - Excel (.xlsx) or CSV files
   - Links labeled "Race Summary" or "Download Data"

3. **Download Files**
   - Right-click on Excel/CSV links
   - Save to: `texas_election_data/raw/`
   - Name clearly: `tx_2020_senate_official.xlsx`

4. **Convert to CSV** (if Excel)
   ```python
   import pandas as pd
   df = pd.read_excel('tx_2020_senate_official.xlsx')
   df.to_csv('tx_2020_senate_official.csv', index=False)
   ```

**Pros:** Official source. Most authoritative. All races.
**Cons:** May require manual work. Inconsistent formats.

---

## ✅ Option 4: Texas Election Results Portal (Requires Browser)

### Access the Interactive Portal

1. **Go to:** https://results.texas-election.com/

2. **Select Election:**
   - Choose year (2020, 2022, or 2024)
   - Choose "General Election"

3. **Export Data:**
   - Look for "Export" or "Download" buttons
   - Some pages have CSV export options
   - You may need to export race-by-race

4. **Alternative - Use Browser Developer Tools:**
   ```javascript
   // In browser console, look for API calls like:
   // https://results.texas-election.com/api/races?year=2024
   // Copy the JSON responses and convert to CSV
   ```

**Pros:** Interactive. Can filter races.
**Cons:** Requires manual clicking. May need to export multiple times.

---

## 🤖 Option 5: Use Selenium (Automated Browser)

If you want to automate the download despite JavaScript requirements:

### Install Selenium
```bash
pip install selenium webdriver-manager
```

### Basic Scraper Script
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Setup Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to results portal
driver.get('https://results.texas-election.com/')

# Wait for page to load
time.sleep(5)

# Find and click export/download buttons
# This requires inspecting the page to find element IDs
export_button = driver.find_element(By.ID, 'export-button-id')
export_button.click()

# Save downloaded file
time.sleep(3)
driver.quit()
```

**Pros:** Fully automated. Can handle JavaScript.
**Cons:** More complex. Requires Chrome driver. May break if site changes.

---

## 📋 Recommended Workflow

### Quick Start (30 minutes):
1. Download MIT Senate and House data (Option 1)
2. Check OpenElections for 2020 precinct data (Option 2)
3. You'll have county-level coverage for 2020-2024

### Complete Dataset (2-3 hours):
1. Visit Texas SOS for each year (Option 3)
2. Download official canvass reports
3. Parse Excel files to CSV
4. Standardize column names to match your existing data

### Best of Both:
1. Use MIT data for quick modeling
2. Supplement with Texas SOS official data for final analysis
3. Add OpenElections precinct data where available

---

## 🔍 What to Download

### Minimum (for modeling):
- **2020:** Senate (Ted Cruz vs. MJ Hegar), Presidential (already have)
- **2022:** Governor (Abbott vs. O'Rourke), All statewide races
- **2024:** Senate (Ted Cruz vs. Colin Allred), Presidential, All statewide

### Ideal (complete dataset):
- **2020:** All races (Pres, Senate, House, State Leg)
- **2022:** All races (Gov, Lt. Gov, AG, House, State Leg)
- **2024:** All races (Pres, Senate, House, State Leg)

### Format Priority:
1. **Precinct-level** (most detailed) - OpenElections
2. **County-level** (good for most models) - MIT / Texas SOS
3. **Statewide aggregate** (least detailed) - Texas SOS

---

## ✅ Verification Checklist

After downloading, verify each file:

```python
import pandas as pd

df = pd.read_csv('your_downloaded_file.csv')

# Check basics
print(f"Rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Check for key columns
required_cols = ['candidate', 'votes', 'party']
for col in required_cols:
    if col not in df.columns:
        print(f"⚠ Missing column: {col}")

# Check for data
print(f"Total votes: {df['votes'].sum():,}")
print(f"Candidates: {df['candidate'].nunique()}")
```

---

## 📞 Need Help?

If you get stuck:
1. Check the OpenElections GitHub issues
2. Look for Texas SOS "Contact" page for data requests
3. Try MIT Election Lab documentation
4. Worst case: manually download PDFs and use OCR (last resort!)

---

**Remember:** You already have great data for 2014-2018! Start modeling with that while you collect 2020-2024 data.
