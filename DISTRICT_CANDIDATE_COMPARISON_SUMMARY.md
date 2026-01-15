# District Candidate vs. Statewide Candidate Comparison

## Overview

We now have a complete system for analyzing **how district-level candidates perform compared to statewide candidates in their districts**. This allows us to identify strong local candidates who could be recruited for statewide races.

---

## What's Being Analyzed

### District-Level Candidates
**Actual races FOR district seats:**
- **State House races**: 150 districts, who ran for State Representative
- **State Senate races**: 31 districts, who ran for State Senator

### Statewide Candidates in Those Districts
**Statewide races (President, U.S. Senate, etc.) broken down BY district:**
- How Trump/Harris performed in State House District 71
- How Cruz/Allred performed in State Senate District 10
- Etc.

### The Comparison
We calculate: **District Candidate % - Statewide Candidate % = Personal Vote**

Example:
- **Mary Ann Morales (D)** won State House District 74 with **51.7%**
- **Kamala Harris (D)** got **42.1%** in that same district
- **Morales outperformed Harris by +9.6 points** in an R+14.8 district!
- This shows Morales has **strong personal appeal and crossover voting**

---

## Key Metrics

### 1. vs_top_ticket
How much better/worse the district candidate performed than the Presidential candidate of their party

- **Positive** = Stronger than top-of-ticket (personal appeal)
- **Negative** = Weaker than top-of-ticket (drag on ballot)
- **Zero** = Matched party baseline

### 2. partisan_lean
District's D-R margin in Presidential race (D% - R%)

- **Positive** = D-leaning district
- **Negative** = R-leaning district
- **Near zero** = Swing district

### 3. favorable_district
Whether district leans toward candidate's party

- D candidate in D+ district = favorable
- R candidate in R+ district = favorable
- D candidate in R+ district = unfavorable (crossover appeal if won!)

### 4. recruitment_score
Composite score for identifying strong statewide prospects:

```
Score =
  (vs_top_ticket × 0.4) +           # Personal brand strength
  ((pct - 50) × 0.3) +              # Margin of victory
  (unfavorable_terrain × 0.3)       # Winning in tough districts
```

---

## Analysis Tools

### `district_candidate_analyzer.py`

**Main Class**: `DistrictCandidateAnalyzer`

#### Key Methods:

##### 1. `calculate_vs_top_ticket(district_level='house')`
Returns DataFrame with every district candidate and their performance vs. Presidential candidate

**Output columns:**
- district, candidate, party, percentage
- top_ticket_candidate, top_ticket_pct
- **vs_top_ticket** (key metric!)
- partisan_lean, favorable_district

##### 2. `identify_strong_candidates(district_level='house', min_vs_top_ticket=2.0, party=None)`
Find candidates who significantly outperformed top-of-ticket

**Parameters:**
- `district_level`: 'house' or 'senate'
- `min_vs_top_ticket`: Minimum outperformance (default 2.0 points)
- `party`: Filter by 'D', 'R', or None

**Example:**
```python
analyzer = DistrictCandidateAnalyzer()
strong_dems = analyzer.identify_strong_candidates(party='D', min_vs_top_ticket=5.0)
# Returns all Democrats who beat Harris by 5+ points in their districts
```

##### 3. `identify_crossover_appeal_candidates(district_level='house', party=None)`
Find candidates who won (or performed well) in **unfavorable districts**

**Logic:**
- D candidates in R-leaning districts who:
  - Won (>50%), OR
  - Lost but outperformed top-of-ticket by 5+ points
- R candidates in D-leaning districts who did the same

**Example:**
```python
crossover = analyzer.identify_crossover_appeal_candidates(party='D')
# Returns Democrats who won in Republican-leaning districts
```

##### 4. `generate_recruitment_report(party, district_level='house')`
Generate ranked list of potential statewide recruitment targets

**Looks for:**
- Winners (>50%)
- Outperformed top-of-ticket
- Strong performance in unfavorable terrain

**Example:**
```python
targets = analyzer.generate_recruitment_report(party='D')
# Returns top Democratic State House members for statewide recruitment
```

---

## 2024 Key Findings

### Top State House Democrats (vs. Harris)

| District | Candidate | Vote % | Harris % | Overperformance | Partisan Lean |
|----------|-----------|--------|----------|-----------------|---------------|
| **74** | **Mary Ann Morales** | **51.7%** | **42.1%** | **+9.6** | **R+14.8** |
| 35 | Oscar Longoria | 100.0% | 45.0% | +55.0 | R+9.2 |
| 38 | Penny Morales Shaw | 100.0% | 46.8% | +53.2 | R+5.4 |
| 144 | Mary Ann Perez | 100.0% | 47.5% | +52.5 | R+3.8 |
| 41 | Bobby Guerra | 53.5% | 47.9% | +5.6 | R+3.2 |
| 39 | Armando Martinez | 60.9% | 48.5% | +12.4 | R+2.1 |

**Key Insight:** Mary Ann Morales (HD-74) is the standout - won a contested race in a strongly Republican district by running 9.6 points ahead of Harris. Classic "strong local brand" candidate with statewide potential.

### Democrats with Crossover Appeal

All 9 Democrats who won in R-leaning districts showed ability to win persuadable voters. These are prime statewide recruitment targets.

### Top State House Republicans (vs. Trump)

| District | Candidate | Vote % | Trump % | Overperformance | Partisan Lean |
|----------|-----------|--------|----------|-----------------|---------------|
| 133 | Denise DeAyala | 100.0% | 52.1% | +47.9 | R+6.3 |
| 126 | Sam Harless | 99.0% | 56.8% | +42.2 | R+15.5 |
| 91 | Stephanie Lowe | 100.0% | 60.2% | +39.8 | R+21.8 |

**Note:** Many of these ran unopposed, which inflates their outperformance numbers. Still indicates these are safe Republican seats with strong incumbents.

### State Senate Analysis

Only 15 of 31 State Senate districts had contested races in 2024:

**Strongest performers:**
- **Juan Hinojosa (D, SD-20)**: 100% (unopposed), Harris got 47.4% - won R+4.3 district
- **Sarah Eckhardt (D, SD-14)**: 100% (unopposed), Harris got 71.8% - very safe D district
- **Royce West (D, SD-23)**: 100% (unopposed), Harris got 72.3% - very safe D district

**Close/competitive:**
- **Morgan LaMantia (D, SD-27)**: Lost 48.3% in R+12.1 district, but outperformed Harris by +4.8 points

---

## Use Cases

### 1. Party Recruitment
**Question:** "Which State House members should we recruit for statewide races?"

```python
analyzer = DistrictCandidateAnalyzer()
targets = analyzer.generate_recruitment_report(party='D', district_level='house')
print(targets.head(20))
```

**Output:** Ranked list by recruitment score - prioritizes:
- Winners in unfavorable districts
- Large overperformance vs. top-of-ticket
- Strong margins

### 2. Opposition Research
**Question:** "Which Republican State Reps are vulnerable because they underperformed Trump?"

```python
weak_rs = analyzer.calculate_vs_top_ticket(district_level='house')
weak_rs = weak_rs[
    (weak_rs['party'] == 'R') &
    (weak_rs['vs_top_ticket'] < 0) &
    (weak_rs['percentage'] < 55)
]
print(weak_rs.sort_values('vs_top_ticket'))
```

### 3. Crossover Appeal Analysis
**Question:** "Show me candidates who can win persuadable voters in hostile territory"

```python
crossover = analyzer.identify_crossover_appeal_candidates(party='D')
print(crossover)
```

### 4. District-Specific Analysis
**Question:** "How did the State Rep in District 71 compare to Cruz and Harris?"

```python
all_results = analyzer.calculate_vs_top_ticket(district_level='house')
district_71 = all_results[all_results['district'] == '71']
print(district_71)
```

---

## Data Sources

### District Races (Red-226 Reports)
- **2024 State House**: 150 PDFs from wrm.capitol.texas.gov (r8.pdf files)
- **2024 State Senate**: 31 PDFs from wrm.capitol.texas.gov (r8.pdf files)
- **Format**: District Election Reports showing actual district race results
- **Parsed to**: `2024_house_races.csv`, `2024_senate_races.csv`

### Statewide Races by District (Red-206 Reports)
- **2024 results**: Statewide races broken down by House/Senate/Congressional districts
- **Format**: Election Analysis reports
- **Parsed to**: `2024_house_district_results.csv`, `2024_senate_results.csv`

---

## Limitations & Future Enhancements

### Current Limitations

1. **2024 data only** for district races
   - Older years (2018, 2020, 2022) require different data sources
   - Many 2024 races were unopposed (inflates overperformance)

2. **Unopposed races**
   - Candidate gets 100%, even if weak
   - Can't distinguish strong incumbents from weak districts
   - Need primary data or previous competitive races

3. **No demographic overlay**
   - Can't see if candidate won due to specific demographic appeal
   - Future: merge with Census data

4. **No spending data**
   - Can't measure efficiency (votes per dollar)
   - Future: integrate campaign finance

### Future Enhancements

#### 1. Multi-Year Analysis
Collect district race data for 2018, 2020, 2022 to:
- Track candidate improvement over time
- Identify trending districts
- See how candidates perform in different environments

#### 2. Primary Election Analysis
Add primary results to:
- Evaluate candidates in contested races (even if general was unopposed)
- Measure intra-party strength
- Identify factional candidates vs. consensus picks

#### 3. Incumbent Analysis
Track:
- Years in office
- Previous competitive races
- Approval ratings
- Committee assignments

#### 4. Campaign Finance
Add spending data to:
- Calculate ROI (votes per dollar)
- Identify efficient candidates
- Measure name recognition vs. spending

#### 5. Demographic Overlays
Merge with Census data:
- Which candidates overperform in Hispanic districts?
- Urban vs. suburban vs. rural patterns
- Education and income correlations

---

## Files

### Analysis Scripts
- `district_candidate_analyzer.py` - Main analysis tool
- `candidate_strength_model.py` - Statewide candidate analysis (original)

### Data Collection
- `download_district_races_2024.py` - Downloads r8.pdf files
- `parse_district_races_2024.py` - Extracts data from PDFs

### Data Files
- `2024_house_races.csv` - 250 candidates, 149 contested races
- `2024_senate_races.csv` - 26 candidates, 15 contested races
- `2024_house_district_results.csv` - Statewide races by House district
- `2024_senate_results.csv` - Statewide races by Senate district

### Documentation
- `DISTRICT_RACE_DATA_SOURCES.md` - Data source documentation
- `DISTRICT_CANDIDATE_COMPARISON_SUMMARY.md` - This file

---

## Example Workflow

### Scenario: Finding 2026 Statewide Candidates

```python
from district_candidate_analyzer import DistrictCandidateAnalyzer

# Initialize
analyzer = DistrictCandidateAnalyzer()

# Get recruitment targets
targets = analyzer.generate_recruitment_report(party='D', district_level='house')

# Filter to top 10
top_10 = targets.head(10)

# Get detailed performance
for _, candidate in top_10.iterrows():
    print(f"\n{candidate['candidate']} (HD-{candidate['district']})")
    print(f"  Won with: {candidate['percentage']:.1f}%")
    print(f"  Harris got: {candidate['top_ticket_pct']:.1f}%")
    print(f"  Overperformance: +{candidate['vs_top_ticket']:.1f} points")
    print(f"  District lean: {'D' if candidate['partisan_lean'] > 0 else 'R'}")
    print(f"    +{abs(candidate['partisan_lean']):.1f}")
    print(f"  Recruitment score: {candidate['recruitment_score']:.1f}")
```

---

**Last Updated:** 2025-01-15
**Data Coverage:** 2024 General Election
**Model Version:** 1.0
