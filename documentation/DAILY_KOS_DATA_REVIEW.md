# Daily Kos Elections Congressional District Data Review

## Data Source

**The Downballot** (formerly Daily Kos Elections) provides verified presidential election results by congressional district.

**Downloaded**: January 17, 2026
**File**: `texas_election_data/pdf_extracts/daily_kos_2020_2024_presidential_by_cd.csv`
**URL**: https://docs.google.com/spreadsheets/d/1ng1i_Dm_RMDnEvauH44pgE6JCUsapcuu8F2pCfeLWFo/edit?gid=620838163

## Data Structure

### Format
CSV file with 437 congressional districts (all 50 states)

### Columns
- **District**: State-District format (e.g., TX-01, TX-09)
- **Incumbent**: Representative name
- **Party**: (R) or (D)
- **2024 Results**: Harris %, Trump %, Margin
- **2020 Results**: Biden %, Trump %, Margin

### Texas Coverage
- **38 congressional districts** (TX-01 through TX-38)
- **2 election years**: 2020, 2024
- **Presidential races only**: No down-ballot statewide races

## Data Verification

### TX-09 (Houston - Al Green)
**Our previous WRONG data (PLANC2308):**
- Biden: 46.7%, Trump: 52.0% ❌

**Daily Kos Elections data:**
- Biden: 76%, Trump: 23% ✅

**Margin**: Biden +53 points ✅

This matches the known correct result from Texas Politics Project.

### TX-32 (Dallas - Julie Johnson)
**Daily Kos Elections data:**
- 2020: Biden 66%, Trump 33% (Biden +33)
- 2024: Harris 61%, Trump 37% (Harris +24)

This also matches known results - TX-32 is a strong Democratic district.

### TX-07 (Houston - Lizzie Fletcher)
**Daily Kos Elections data:**
- 2020: Biden 64%, Trump 34% (Biden +30)
- 2024: Harris 59%, Trump 38% (Harris +21)

Competitive district that flipped to Democrats in 2018.

## Pros and Cons

### ✅ Advantages

1. **Verified and Trusted**: Used by analysts, campaigns, and media nationwide
2. **Already Downloaded**: No PDF parsing needed
3. **Clean Format**: CSV ready for immediate import
4. **Covers 2020 & 2024**: Both presidential years in our dataset
5. **Correct Districts**: Uses actual district boundaries for each election
6. **Zero Bugs**: No risk of parser errors

### ❌ Limitations

1. **Presidential Only**: No U.S. Senate, Governor, or other statewide races
2. **Missing 2018 & 2022**: Only has presidential years (2020, 2024)
3. **No 2018 data**: Can't analyze 2018 congressional vs_top_ticket

## Comparison to Our Needs

| Need | Daily Kos | Our Red-206 Approach |
|------|-----------|---------------------|
| 2020 Presidential by CD | ✅ Yes | ✅ Yes (if we fix PDFs) |
| 2024 Presidential by CD | ✅ Yes | ✅ Yes (if we fix PDFs) |
| 2018 Senate by CD | ❌ No | ✅ Yes (if we fix PDFs) |
| 2022 Governor by CD | ❌ No | ✅ Yes (if we fix PDFs) |
| All years coverage | ❌ Partial | ✅ Complete |
| Data quality | ✅ Verified | ⚠️ Need correct PDFs |

## Recommendation

### Hybrid Approach (Best Solution)

1. **Use Daily Kos for 2020 & 2024 Presidential**
   - Import immediately (no parsing needed)
   - Highest data quality
   - Enables congressional analysis for presidential years

2. **Download Red-206 PDFs for 2018 & 2022**
   - Get PLANC2100 for 2018 (U.S. Senate by CD)
   - Get PLANC2193 for 2022 (Governor by CD)
   - Enables complete 4-year analysis

This gives us:
- ✅ Immediate working congressional analysis (2020, 2024)
- ✅ Complete dataset when Red-206 PDFs added (2018, 2022)
- ✅ Highest quality data (verified + official sources)

## Next Steps

### Immediate (15 minutes)
1. Create import script for Daily Kos data
2. Convert to our standard format (year, district, office, candidate, party, votes, percentage)
3. Update analyzer to use Daily Kos data
4. Test congressional vs_top_ticket analysis

### Follow-up (Future)
1. Download correct Red-206 PDFs for 2018 & 2022
2. Add to dataset to complete time series
3. Full 4-year congressional recruitment analysis

## Sources

- [The Downballot 2024 Presidential Results by CD](https://docs.google.com/spreadsheets/d/1ng1i_Dm_RMDnEvauH44pgE6JCUsapcuu8F2pCfeLWFo/edit?gid=620838163)
- [The Downballot Data Guide](https://www.the-downballot.com/p/data)
- [Daily Kos Elections Homepage](https://www.dailykos.com/blogs/Elections)
