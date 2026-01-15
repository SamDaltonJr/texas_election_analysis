# Multi-Year District Candidate Analysis with Competitiveness Flags

## Overview

The new `district_candidate_analyzer_multiyear.py` extends the original analysis to support **all four election cycles (2018-2024)** and adds **critical competitiveness flags** to distinguish truly strong candidates from those who simply ran unopposed or against weak opposition.

---

## Why Competitiveness Flags Matter

### The Problem

Without filtering, a candidate who runs **unopposed** and gets 100% looks like they "outperformed" the top-of-ticket by 40+ points. But this is misleading:

**Example:**
- Oscar Longoria (HD-35, 2024): 100% vs. Harris: 45% = +55 points!
- BUT: He ran **unopposed** (no Republican candidate)
- This doesn't prove personal strength, just lack of competition

### The Solution

We now classify each race by multiple dimensions:

1. **has_major_party_opponent**: Did the race have both D and R candidates?
2. **is_contested**: More than one candidate (any party)?
3. **is_competitive**: Winning margin < 20 points?
4. **opposition_strength**: 'strong', 'moderate', 'weak', or 'none'
5. **winning_margin**: Percentage point difference between top two candidates

---

## Competitiveness Classification

### opposition_strength Categories

**'none'** - Unopposed
- Only one candidate
- Gets 100% by default
- Example: Longoria (HD-35, 2024) - 100%, unopposed

**'weak'** - Minor party or large margin
- Either: No major party opponent (L, I, G only)
- Or: Major party opponent but won by 20+ points
- Example: Raymond (HD-42, 2022) - Won by 42.4 points vs R

**'moderate'** - Competitive but not close
- Both major parties present
- Won by 10-20 points
- Example: Morales (HD-74, 2022) - Won by 11.4 points vs R

**'strong'** - Highly competitive
- Both major parties present
- Won by < 10 points
- Example: Beckley (HD-65, 2020) - Won by 3.0 points vs R

---

## How to Use the Multi-Year Analyzer

### Basic Usage

```python
from district_candidate_analyzer_multiyear import MultiYearDistrictCandidateAnalyzer

analyzer = MultiYearDistrictCandidateAnalyzer()

# Find strong Democrats with real opposition
strong = analyzer.identify_strong_candidates(
    district_level='house',
    year=2022,
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True,  # Only races with both D and R
    require_contested=True               # Only races with multiple candidates
)
```

### Key Methods

#### 1. `identify_strong_candidates()`

Find candidates who outperformed top-of-ticket, with competitiveness filters.

**Parameters:**
- `district_level`: 'house' or 'senate'
- `year`: Specific year (2018, 2020, 2022, 2024) or None for all
- `min_vs_top_ticket`: Minimum outperformance (default 2.0 points)
- `party`: 'D', 'R', or None
- `require_major_party_opponent`: Filter to races with both D and R (default True)
- `require_contested`: Filter to races with 2+ candidates (default True)

**Example:**
```python
# Find 2022 Democrats who beat O'Rourke by 5+ in real races
strong_2022 = analyzer.identify_strong_candidates(
    year=2022,
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True
)
```

#### 2. `identify_crossover_appeal_candidates()`

Find candidates who won in unfavorable districts (with real opposition).

**Example:**
```python
# Democrats who won R-leaning districts (real opposition only)
crossover = analyzer.identify_crossover_appeal_candidates(
    year=2022,
    party='D',
    require_major_party_opponent=True
)
```

#### 3. `track_candidate_over_time()`

Follow a specific candidate across multiple elections.

**Example:**
```python
# Track Lambert's performance 2020-2024
lambert = analyzer.track_candidate_over_time('Lambert', district_level='house')
```

**Output includes:**
- Performance in each year
- vs_top_ticket for each year
- Competitiveness flags for each race
- Winning margins

#### 4. `compare_years()`

Compare party performance between two years.

**Example:**
```python
# See which districts improved for Democrats 2018 → 2022
comparison = analyzer.compare_years(2018, 2022, party='D')
```

#### 5. `calculate_vs_top_ticket()`

Core method that returns full DataFrame with all metrics and flags.

**Example:**
```python
# Get all data for manual analysis
df = analyzer.calculate_vs_top_ticket(district_level='house', year=2022)

# Filter to your needs
strong_competitive = df[
    (df['vs_top_ticket'] > 5) &
    (df['opposition_strength'] == 'strong')
]
```

---

## Key Findings from Multi-Year Analysis

### 1. True Crossover Champions (Strong Opposition)

**Democrats who won R-leaning districts with major party opposition:**

**2022:**
- **Mary Ann Morales (HD-74)**: Won 55.7% in R+0.3 district, beat O'Rourke by +6.8
  - Only Democrat to flip an R-lean with strong opposition in 2022!

**2020:**
- **Erin Zwiener (HD-45)**: Won R-leaning district with strong opposition
- **Yvonne Davis (HD-111)**: Strong performance in competitive district
- **Michelle Beckley (HD-65)**: Won by 3 points in R+8 district (+6.4 vs Biden)

**2018:**
- Multiple Democrats won competitive districts in the "blue wave" year

### 2. Strongest Overperformers (All Years, Real Opposition)

| Year | District | Candidate | vs_top_ticket | Opposition | Partisan Lean |
|------|----------|-----------|---------------|------------|---------------|
| 2020 | HD-31 | Guillen | +21.3 | moderate | R+25 |
| 2024 | HD-39 | Martinez | +12.4 | weak | R+2.1 |
| 2022 | HD-42 | Raymond | +11.2 | weak | D+22 |
| 2022 | HD-35 | Longoria | +10.3 | weak | D+9 |
| 2024 | HD-74 | Morales | +9.6 | **strong** | R+15 |

**Note:** Guillen's 2020 performance stands out - massive overperformance in deep R territory with real opposition.

### 3. Consistent Performers

**Lambert (HD-71, R)**: Ran in 2020, 2022, 2024
- Always wins 78-81%
- Always beats top-of-ticket by 2-4 points
- But: Always weak opposition (wins by 58-62 points)
- Verdict: Strong incumbent, but untested against serious challenge

### 4. Party Trends by Competitiveness

**2022 (Abbott vs O'Rourke):**
- **With major party opposition:** Only 1 Democrat won an R-leaning district (Morales)
- **Without major party opposition:** 10+ Democrats "outperformed" in R-districts
- **Takeaway:** Republicans successfully recruited candidates in competitive districts

**2020 (Trump vs Biden):**
- **With major party opposition:** Several Democrats won R-lean districts
- **High competition:** Democrats won 3+ districts with <10 point margins
- **Takeaway:** Better Democratic recruitment/environment than 2022

---

## Recruitment Implications

### High-Priority Targets (Proven in Battle)

**Mary Ann Morales (HD-74)**
- **Years**: 2022, 2024
- **2022**: Won R+0.3 district by 11.4 points with R opponent
- **2024**: Won R+15 district by 3.4 points with R opponent
- **Verdict**: Proven crossover appeal, won tough districts twice
- **Statewide Potential**: ⭐⭐⭐⭐⭐ (highest)

**Armando Martinez (HD-39)**
- **Years**: 2020, 2022, 2024
- **Best**: 2024 beat Harris by +12.4 in R+2 district
- **Verdict**: Consistent winner in swing district
- **Statewide Potential**: ⭐⭐⭐⭐

### Caution: Untested Strength

**Oscar Longoria (HD-35)**
- Huge overperformance numbers (+55 in 2024)
- BUT: Ran unopposed in 2024
- 2022: Won with weak opposition
- **Verdict**: Strong district, but personal appeal unclear
- **Statewide Potential**: ⭐⭐⭐ (need to see real competition)

**Alex Raymond (HD-42)**
- Massive margins (+11.2 vs O'Rourke in 2022)
- BUT: D+22 district, won by 42 points
- **Verdict**: Safe seat, no evidence of crossover appeal
- **Statewide Potential**: ⭐⭐ (not tested in hostile territory)

---

## Filtering Best Practices

### For Statewide Recruitment

**Recommended filters:**
```python
strong_candidates = analyzer.identify_strong_candidates(
    year=2022,
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True,  # Must face R opponent
    require_contested=True
)

# Further filter to competitive races
strong_tested = strong_candidates[
    strong_candidates['opposition_strength'].isin(['strong', 'moderate'])
]
```

### For Opposition Research

**Find vulnerable incumbents:**
```python
# Get all data
df = analyzer.calculate_vs_top_ticket(district_level='house', year=2024)

# Find Republicans who:
# 1. Underperformed Trump
# 2. Had real opposition
# 3. Won by < 15 points
vulnerable = df[
    (df['party'] == 'R') &
    (df['vs_top_ticket'] < 0) &
    (df['has_major_party_opponent'] == True) &
    (df['winning_margin'] < 15)
]
```

### For Historical Analysis

**Compare same district over time:**
```python
# HD-74 across all years
hd74 = analyzer.calculate_vs_top_ticket(district_level='house')
hd74 = hd74[hd74['district'] == '74']

# See how Morales improved 2022 → 2024
print(hd74[['year', 'candidate', 'percentage', 'vs_top_ticket',
           'opposition_strength']].sort_values('year'))
```

---

## Data Quality by Filter

### All Candidates (No Filters)
- **Count**: 906 House candidates across 4 years
- **Includes**: Unopposed, third-party only, all races
- **Use for**: General overview, completeness

### Contested Races Only
- **Count**: ~700 House candidates
- **Excludes**: Unopposed races
- **Use for**: Comparing actual competitive performance

### Major Party Opposition Only
- **Count**: ~600 House candidates
- **Excludes**: Unopposed + third-party only races
- **Use for**: Realistic statewide recruitment analysis

### Strong/Moderate Opposition Only
- **Count**: ~200 House candidates
- **Excludes**: Weak opposition (20+ point margins)
- **Use for**: Identifying truly battle-tested candidates

---

## Output Columns

All analysis methods return DataFrames with these key columns:

**Identity:**
- `year`, `district`, `district_type`, `candidate`, `party`

**Performance:**
- `votes`, `percentage`, `top_ticket_pct`, `vs_top_ticket`

**District:**
- `partisan_lean`, `partisan_lean_strength`, `favorable_district`

**Competitiveness (NEW):**
- `has_major_party_opponent`: Boolean
- `is_contested`: Boolean
- `is_competitive`: Boolean (margin < 20 points)
- `winning_margin`: Float (percentage points)
- `opposition_strength`: 'strong', 'moderate', 'weak', 'none'

---

## Examples

### Example 1: Find Rising Stars

```python
analyzer = MultiYearDistrictCandidateAnalyzer()

# Get all strong performances with real opposition
strong = analyzer.identify_strong_candidates(
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True
)

# Group by candidate to find those who consistently outperform
by_candidate = strong.groupby('candidate').agg({
    'year': 'count',  # Number of strong performances
    'vs_top_ticket': 'mean',  # Average overperformance
    'opposition_strength': lambda x: list(x)  # Opposition faced
}).rename(columns={'year': 'num_elections'})

# Filter to 2+ strong performances
rising_stars = by_candidate[by_candidate['num_elections'] >= 2]
print(rising_stars.sort_values('vs_top_ticket', ascending=False))
```

### Example 2: District Competitiveness Trends

```python
# Get HD-74 over time
hd74_all_years = analyzer.calculate_vs_top_ticket(district_level='house')
hd74 = hd74_all_years[hd74_all_years['district'] == '74']

# See partisan lean changes
print(hd74[['year', 'partisan_lean', 'has_major_party_opponent']].drop_duplicates())

# 2018: R+14 (Republican lean)
# 2020: R+10 (Moving left)
# 2022: R+0.3 (Nearly even!)
# 2024: R+15 (Swung back right)
```

### Example 3: Recruitment Report with Filters

```python
# Generate recruitment targets for Democrats
targets = analyzer.identify_strong_candidates(
    party='D',
    min_vs_top_ticket=5.0,
    require_major_party_opponent=True
)

# Score candidates
targets['recruitment_score'] = (
    targets['vs_top_ticket'] * 0.4 +
    (targets['percentage'] - 50) * 0.3 +
    np.where(targets['partisan_lean'] < 0,
             targets['partisan_lean_strength'], 0) * 0.3
)

# Filter to winners in tested races
winners = targets[
    (targets['percentage'] > 50) &
    (targets['opposition_strength'].isin(['strong', 'moderate']))
]

print(winners.sort_values('recruitment_score', ascending=False).head(10))
```

---

## Files

**Script:** `district_candidate_analyzer_multiyear.py`
**Data:** Uses all existing CSV files (2018-2024, House and Senate)
**Documentation:** This file

---

**Model Version:** 2.0 (Multi-Year with Competitiveness Flags)
**Last Updated:** 2025-01-15
**Data Coverage:** 2018-2024 (4 election cycles)
