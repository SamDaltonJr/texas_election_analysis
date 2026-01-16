# Repository Cleanup - January 2026

## Files Removed

### Temporary/Debug Files
- All `tmpclaude-*` directories (100+ temporary working directories)
- `sample_2018_house_districts.pdf`
- `temp_congress_dist1_r5.pdf`
- `temp_congress_dist1_r8.pdf`
- `temp_r8_sample.pdf`
- `temp_senate_dist1_r8.pdf`
- Python `__pycache__` directories

### Incorrect Source PDFs (Wrong District Plans)
**Congressional (PLANC2308 - hypothetical redistricting):**
- `2018_congressional_c2308.pdf`
- `2020_congressional_c2308.pdf`
- `2022_congressional_c2308.pdf`
- `2024_congressional_c2308.pdf`

**Senate (wrong plans or failed downloads):**
- `2018_senate_s2168.pdf` (should use PLANS172)
- `2020_senate_s2168.pdf` (should use PLANS172)
- `2022_senate_s2168.pdf` (duplicate, kept CORRECT version)
- `2024_senate_s2168.pdf` (duplicate, kept CORRECT version)

**Failed Downloads:**
- `2018_congressional_PLANC235_r206.pdf` (5KB redirect file)
- `2020_congressional_PLANC235_r206.pdf` (5KB redirect file)
- `2020_congressional_PLANC2100_r206.pdf`

### Incorrect Data Files
- `2018_2024_congressional_results_combined_INCORRECT_DO_NOT_USE.csv`
- `2018_2024_senate_results_combined_INCORRECT_DO_NOT_USE.csv`

### Unnecessary Scripts
- `data_collection/fix_congressional_statewide_data.py` (one-time fix script)

### Raw/Intermediate Files
- `raw_extract_2018.txt`
- `temp_plans172_test.pdf`
- `texas_election_2018.pdf`
- `2024_sample.pdf`

## Files Kept (Correct/Active)

### State Senate PDFs (CORRECT)
- `2018_senate_PLANS172_r206.pdf` - 2018 Senate races (actual districts)
- `2020_senate_PLANS172_r206.pdf` - 2020 Senate races (actual districts)
- `2022_senate_PLANS2168_r206_CORRECT.pdf` - 2022 Senate races
- `2024_senate_PLANS2168_r206_CORRECT.pdf` - 2024 Senate races

### State House PDFs (CORRECT)
- `2020_planh2176.pdf`, `2022_planh2176.pdf`, `2024_planh2176.pdf`
- `2020_planh2316.pdf`, `2022_planh2316.pdf`, `2024_planh2316.pdf`
- `2022_planh2176_full.pdf`, `2024_planh2176_full.pdf`

### Correct Data Files
- `2018_2024_senate_results_combined_CORRECT.csv` - Verified Senate statewide results
- All house district results CSVs
- All race results CSVs

### Active Scripts
- `data_collection/parse_senate_districts_CORRECT.py` - Senate parser
- All other collection and analysis scripts

## New Files Added
- `.gitignore` - Prevents future temporary files from being committed

## Impact
- Removed ~100+ temporary directories
- Removed ~20 incorrect/duplicate PDF files
- Cleaned up repository structure for maintainability
- All analysis functionality preserved with correct data sources
