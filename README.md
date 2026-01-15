# Texas Election Analysis System

A comprehensive system for analyzing Texas election data (2018-2024) across State House, State Senate, and U.S. Congressional districts. Identifies candidate strength, crossover appeal, and statewide recruitment prospects.

## Quick Start

### Interactive Analysis (Recommended)

```bash
# Open Jupyter notebooks
jupyter notebook notebooks/02_multiyear_district_candidate_analysis.ipynb
```

### Command Line Analysis

```python
from analysis_tools.district_candidate_analyzer_multiyear import MultiYearDistrictCandidateAnalyzer

# Initialize analyzer
analyzer = MultiYearDistrictCandidateAnalyzer()

# Find strong Democrats with real opposition
strong = analyzer.identify_strong_candidates(
    year=2024,
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True
)
```

## Project Structure

```
texas_election_analysis/
│
├── analysis_tools/           # Core analysis modules
│   ├── candidate_strength_model.py
│   ├── district_candidate_analyzer.py
│   └── district_candidate_analyzer_multiyear.py
│
├── data_collection/          # Data download and parsing scripts
│   ├── download_*.py         # Download PDFs and VTD datasets
│   ├── parse_*.py            # Parse PDFs and aggregate VTD data
│   └── verify_*.py           # Data validation scripts
│
├── notebooks/                # Interactive Jupyter notebooks
│   ├── 01_candidate_strength_exploration.ipynb
│   └── 02_multiyear_district_candidate_analysis.ipynb
│
├── documentation/            # Detailed documentation
│   ├── MULTIYEAR_ANALYSIS_WITH_COMPETITIVENESS.md
│   ├── COMPLETE_DISTRICT_RACE_DATA.md
│   └── TALARICO_CROCKETT_COMPARISON.md
│
└── texas_election_data/      # Parsed election data (CSV files)
    └── pdf_extracts/
        ├── 2018_2024_house_district_results_all.csv
        ├── 2018_2022_house_races.csv
        ├── 2024_house_races.csv
        └── [50+ additional CSV files]
```

## What's Inside

### 📊 Analysis Tools (`analysis_tools/`)

**Main Analysis Modules:**

1. **`district_candidate_analyzer_multiyear.py`** ⭐ **PRIMARY TOOL**
   - Multi-year analysis (2018-2024)
   - Competitiveness filtering (strong/moderate/weak opposition)
   - Crossover appeal detection
   - Candidate tracking across elections
   - Recruitment scoring

2. **`candidate_strength_model.py`**
   - Original statewide candidate analysis
   - Compares statewide candidates to top-of-ticket
   - Used for analyzing President, U.S. Senate, Governor races

3. **`district_candidate_analyzer.py`**
   - Single-year district analysis (2024 only)
   - Simpler version of multiyear analyzer

### 📥 Data Collection (`data_collection/`)

**Download Scripts:**
- `download_district_races_2024.py` - Downloads 181 district race PDFs (Red-226)
- `download_senate_pdfs_confirmed.py` - Downloads State Senate PDFs
- `download_vtd_datasets.py` - Downloads VTD datasets (200MB)

**Parsing Scripts:**
- `parse_district_races_2024.py` - Parses 2024 district PDFs
- `parse_vtd_district_races.py` - Aggregates VTD data for 2018-2022
- `parse_congressional_races.py` - Parses U.S. House races
- `parse_all_years.py` - Parses statewide races by House district
- `parse_congressional_districts.py` - Parses statewide races by Congressional district
- `parse_senate_districts.py` - Parses statewide races by State Senate district

**Verification Scripts:**
- `verify_data.py` - Validates House district data
- `verify_senate_data.py` - Validates Senate district data
- `verify_congressional_data.py` - Validates Congressional data

### 📓 Interactive Notebooks (`notebooks/`)

1. **`02_multiyear_district_candidate_analysis.ipynb`** ⭐ **START HERE**
   - Multi-year candidate tracking
   - Visualizations and charts
   - Search for any candidate
   - Compare candidates side-by-side
   - Includes Talarico & Crockett examples

2. **`01_candidate_strength_exploration.ipynb`**
   - Original single-year analysis (2024)
   - Statewide candidate comparisons
   - Cruz vs Allred deep dive

### 📚 Documentation (`documentation/`)

**Getting Started:**
- `MULTIYEAR_ANALYSIS_WITH_COMPETITIVENESS.md` - Main guide, start here!
- `COMPLETE_DISTRICT_RACE_DATA.md` - Data collection overview

**Example Analyses:**
- `TALARICO_CROCKETT_COMPARISON.md` - Detailed candidate comparison
- `DISTRICT_CANDIDATE_COMPARISON_SUMMARY.md` - 2024 analysis methodology

**Data Sources:**
- `DISTRICT_RACE_DATA_SOURCES.md` - Where data comes from
- `PDF_DATA_SOURCES.md` - PDF report types explained

### 💾 Data Files (`texas_election_data/pdf_extracts/`)

**District Race Results (Actual races FOR districts):**
- `2024_house_races.csv` - 250 State House candidates (2024)
- `2024_senate_races.csv` - 26 State Senate candidates (2024)
- `2018_2022_house_races.csv` - 656 State House candidates (3 years)
- `2018_2022_senate_races.csv` - 112 State Senate candidates (3 years)
- `2018_2024_congressional_races.csv` - 389 U.S. House candidates (4 years)

**Statewide Races by District (Statewide races broken down BY district):**
- `2018_2024_house_district_results_all.csv` - Statewide results by House district
- `2018_2024_senate_results_combined.csv` - Statewide results by Senate district
- `2018_2024_congressional_results_combined.csv` - Statewide results by Congressional district

## Key Features

### 🎯 Multi-Year Tracking

Track individual candidates across multiple elections:
```python
talarico = analyzer.track_candidate_over_time('Talarico', district_level='house')
```

### 🏆 Competitiveness Filtering

Filter races by opposition quality:
- **Strong**: Won by < 10 points with major party opponent
- **Moderate**: Won by 10-20 points with major party opponent
- **Weak**: Won by 20+ points OR only third-party opposition
- **None**: Unopposed

```python
strong = analyzer.identify_strong_candidates(
    require_major_party_opponent=True  # Only real races
)
```

### 🔄 Crossover Appeal Detection

Find candidates who won in hostile territory:
```python
crossover = analyzer.identify_crossover_appeal_candidates(
    party='D',
    require_major_party_opponent=True
)
```

### 📈 Recruitment Scoring

Rank candidates for statewide potential:
```python
targets = analyzer.generate_recruitment_report(party='D')
```

## Data Coverage

### Election Cycles
- ✅ 2024 General Election
- ✅ 2022 General Election
- ✅ 2020 General Election
- ✅ 2018 General Election

### Geographic Levels
- ✅ State House (150 districts)
- ✅ State Senate (31 districts)
- ✅ U.S. Congressional (38 districts)

### Total Records
- **1,044** district race records (actual State House/Senate races)
- **389** congressional race records (actual U.S. House races)
- **6,191** statewide results by House district
- **1,696** statewide results by Senate district
- **2,067** statewide results by Congressional district

## Example Use Cases

### 1. Find Rising Stars

```python
# Democrats who consistently outperform top-of-ticket
strong_all_years = analyzer.identify_strong_candidates(
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True
)
```

### 2. Identify Vulnerable Incumbents

```python
# Republicans who underperformed Trump with real opposition
df = analyzer.calculate_vs_top_ticket(year=2024)
vulnerable = df[
    (df['party'] == 'R') &
    (df['vs_top_ticket'] < 0) &
    (df['has_major_party_opponent'] == True) &
    (df['winning_margin'] < 15)
]
```

### 3. Track Candidate Improvement

```python
# See how a candidate performed over time
candidate_history = analyzer.track_candidate_over_time('Morales')
```

### 4. Compare Districts

```python
# See which districts are trending
comparison = analyzer.compare_years(2018, 2024, party='D')
```

## Key Metrics Explained

### vs_top_ticket
How much better/worse the candidate performed vs. Presidential/Governor candidate
- **Positive** = Outperformed (strong personal brand)
- **Negative** = Underperformed
- **Zero** = Matched party baseline

### partisan_lean
District's D-R margin in Presidential/Governor race
- **Positive** = D-leaning district
- **Negative** = R-leaning district
- **Near zero** = Swing district

### recruitment_score
Composite score for statewide potential:
```
Score = (vs_top_ticket × 0.4) +
        ((percentage - 50) × 0.3) +
        (unfavorable_terrain × 0.3)
```

## Installation

### Requirements
```bash
pip install pandas numpy matplotlib seaborn pdfplumber requests
```

### Jupyter (for notebooks)
```bash
pip install jupyter
```

## Reproducing the Data

All data can be regenerated from source:

```bash
# 1. Download 2024 PDFs (181 files)
python data_collection/download_district_races_2024.py

# 2. Download VTD datasets (200MB)
python data_collection/download_vtd_datasets.py

# 3. Parse everything
python data_collection/parse_district_races_2024.py
python data_collection/parse_vtd_district_races.py
python data_collection/parse_congressional_races.py
python data_collection/parse_all_years.py
python data_collection/parse_congressional_districts.py
python data_collection/parse_senate_districts.py
```

## Key Findings

### Strongest Crossover Candidates (2020-2024)

**Democrats with proven ability to win R-leaning districts:**
1. **Eddie Morales (HD-74)** - Won R+15 district with R opponent (2024)
2. **Ryan Guillen (HD-31)** - Beat Biden by +21 in R+25 district (2020)
3. **Michelle Beckley (HD-65)** - Won R+8 district by 3 points (2020)

### Candidate Comparisons

**James Talarico** (State House):
- 2020: Won R+4.3 district, outperformed Biden by +4.7 ⭐
- Proven crossover appeal in competitive race
- Now in safe D+49 district

**Jasmine Crockett** (U.S. House):
- 2022: Won D+30 district with 74.7%
- 2024: Won 84.9% (no R opponent)
- Strong but untested in hostile territory

## Contributing

This is a research project. To contribute:
1. Fork the repository
2. Add your analysis or improvements
3. Submit a pull request

## Data Sources

- **Texas Legislative Council** - Red-226 District Election Reports
- **Texas Capitol Data Portal** - Comprehensive VTD Datasets
- **Texas Secretary of State** - Official election results

## License

Data is from public sources. Analysis code is open for educational/research use.

## Citation

If you use this analysis in research or reporting:
```
Texas Election Analysis System (2025)
https://github.com/SamDaltonJr/texas_election_analysis
Data: Texas Legislative Council, Texas Capitol Data Portal (2018-2024)
```

---

**Last Updated:** 2025-01-15
**Data Coverage:** 2018-2024 General Elections
**Version:** 2.0 (Multi-Year with Competitiveness Flags)
