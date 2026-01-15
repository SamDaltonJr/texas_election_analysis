# Candidate Strength Analysis Model

## Overview

This model analyzes individual candidate strength by comparing district-level performance to statewide baseline results, identifying candidates who perform better or worse than expected based on:

1. **Partisan Baseline** - District partisan lean (how D/R the district typically votes)
2. **Top-of-Ticket Performance** - Comparison to Presidential/Gubernatorial candidates
3. **Statewide Environment** - How the candidate did vs. their own statewide average
4. **Incumbency Status** - Whether the candidate has incumbent advantage
5. **Geographic Breadth** - Consistency and reach across diverse districts

---

## Key Findings from 2024 Analysis

### 2024 U.S. Senate Race: Cruz vs. Allred

**Colin Allred (D) - STRONGER CANDIDATE**
- **Overall Strength Score**: -2.99 (less negative = stronger)
- **vs. Top-of-Ticket**: +2.34 points better than Harris
- **Performance**: Outperformed Harris in 150 districts, showing strong personal brand
- **Crossover Appeal**: Performed -8.22 in opposite-lean districts (moderate crossover)
- **Assessment**: **Strong challenger** - significantly outperformed top of ticket

**Ted Cruz (R) - WEAKER INCUMBENT**
- **Overall Strength Score**: -6.41 (more negative = weaker)
- **vs. Top-of-Ticket**: -3.27 points worse than Trump
- **Performance**: Underperformed Trump across most districts
- **Crossover Appeal**: -21.25 in opposite-lean districts (poor crossover)
- **Assessment**: **Vulnerable incumbent** - dragged down by Trump, limited personal appeal

### Key Insight: Allred's Personal Vote

Allred performed **+2.34 points better** than Harris statewide, while Cruz performed **-3.27 points worse** than Trump. This **5.6-point swing** demonstrates:

1. **Allred ran a strong campaign** with significant crossover appeal
2. **Cruz is weaker than the partisan baseline**, suggesting vulnerability
3. **Despite losing, Allred built a foundation** for future races

---

## Cruz: Performance Decline (2018 vs. 2024)

### 2018 U.S. Senate (vs. O'Rourke)
- **Margin**: Cruz +2.6 points (50.9% vs. 48.3%)
- **vs. Top-of-Ticket**: -4.82 (underperformed Abbott by 4.8 points)
- **Strength Score**: -5.26
- **Districts Won**: 84 of 150

### 2024 U.S. Senate (vs. Allred)
- **Margin**: Cruz +4.3 points (53.1% vs. 44.6%)
- **vs. Top-of-Ticket**: -3.27 (underperformed Trump by 3.3 points)
- **Strength Score**: -6.41 (WORSE than 2018)
- **Districts Won**: 84 of 150

### Analysis

While Cruz won by a larger margin in 2024, his **strength score actually declined**:

1. **2024 win due to stronger environment** - Trump +12.2 nationally helped all Republicans
2. **Cruz still underperforms party baseline** - Lost ground relative to top of ticket
3. **Personal brand weakness persists** - Consistently negative strength scores
4. **Vulnerability remains** - Against stronger candidates or in better D environment, Cruz is at risk

---

## O'Rourke: Strong 2018, Weak 2022

### 2018 U.S. Senate (vs. Cruz)
- **Margin**: Lost by 2.6 points
- **vs. Top-of-Ticket**: +5.69 (OUTPERFORMED Valdez by 5.7 points!)
- **Strength Score**: +1.39 (POSITIVE = strong candidate)
- **Districts Won**: 66 of 150
- **Assessment**: **Very strong challenger** - nearly won despite R-lean state

### 2022 Governor (vs. Abbott)
- **Margin**: Lost by 10.9 points
- **vs. Top-of-Ticket**: 0.00 (top of ticket himself)
- **Strength Score**: -4.39 (NEGATIVE = weak candidate)
- **Districts Won**: 64 of 150
- **Assessment**: **Weak statewide candidate** - couldn't build winning coalition

### What Changed?

1. **2018**: O'Rourke was fresh, energetic, outperformed party baseline significantly
2. **2022**: After failed presidential run, O'Rourke was overexposed, nationalized
3. **Lost crossover appeal**: 2018 he won persuadable voters, 2022 he didn't
4. **Abbott stronger than Cruz**: Faced tougher opponent in 2022

---

## Model Methodology

### 1. Partisan Baseline Calculation

**District Partisan Lean** = How the district voted in most recent Presidential race
- Uses 2-party vote share (D vs R only)
- Calculates D-R margin for each district
- Example: District voted Biden +15 → D+15 lean

### 2. Candidate Performance Metrics

**vs. Statewide** = Candidate's district % - Candidate's statewide %
- Shows geographic variation in support
- Positive = performed better than statewide average in this district
- Negative = performed worse

**vs. Top-of-Ticket** = Candidate's % - Presidential/Gubernatorial candidate %
- Measures personal vote beyond party
- Positive = outperformed party (strong personal brand)
- Negative = underperformed party (weak personal brand)

### 3. Strength Score Formula

```
Overall Strength Score =
    (0.4 × Weighted Overperformance) +
    (0.3 × vs. Top-of-Ticket) +
    (0.2 × (Statewide % - 50)) +
    (-0.1 × Standard Deviation of Performance)
```

**Components**:
- **Weighted Overperformance** (40%): Performance vs. statewide, with 2x weight for opposite-lean districts
- **vs. Top-of-Ticket** (30%): How much better/worse than party baseline
- **Statewide Performance** (20%): Raw vote percentage (above/below 50%)
- **Consistency Penalty** (10%): Lower std dev = more consistent (better)

**Interpretation**:
- **Positive score**: Strong candidate, performed better than expected
- **Negative score**: Weak candidate, performed worse than expected
- **Higher absolute value**: Stronger personal brand effect

### 4. Crossover Appeal

**Overperformance in Opposite Districts** = Average vs. Statewide in unfavorable districts
- Republican in D-lean districts or Democrat in R-lean districts
- Positive = winning persuadable voters (critical for statewide wins)
- Negative = doing worse than statewide average in tough districts

---

## Using the Model

### Example 1: Evaluate Incumbent Vulnerability

```python
analyzer = CandidateStrengthAnalyzer(geographic_level='house')

# Analyze 2024 Senate race
senate_2024 = analyzer.analyze_race(2024, 'U.S. Senate')
print(senate_2024[['candidate', 'overall_strength_score', 'avg_vs_top_ticket']])
```

**Result**: Cruz shows negative strength score and underperforms top-of-ticket → Vulnerable incumbent

### Example 2: Compare Candidate Across Elections

```python
# Track Cruz over time
cruz_history = analyzer.compare_candidates_across_elections('Cruz')
```

**Result**: Cruz's strength score declined 2018→2024 despite winning by more → Environment helped, not personal strength

### Example 3: Find Strong Districts for Candidate

```python
# Get Cruz's detailed district performance
cruz_detailed = analyzer.calculate_candidate_performance(2024, 'U.S. Senate', 'Cruz')

# Find overperforming districts
best_districts = cruz_detailed.nlargest(20, 'vs_top_ticket')
```

**Use Case**: Target persuadable districts where candidate has unique appeal

---

## Model Limitations

1. **No Demographic Data**: Model doesn't directly account for district demographics
   - Could be enhanced with Census data overlay
   - Currently uses partisan lean as proxy

2. **Incumbency is Binary**: Doesn't account for strength/length of incumbency
   - Future: Add years in office, approval ratings

3. **National Environment Proxy**: Uses top-of-ticket as environment indicator
   - Could add generic ballot, presidential approval

4. **District Boundary Changes**: 2021 redistricting affects comparisons
   - 2018/2020 use old boundaries (PLANH2316)
   - 2022/2024 use new boundaries (PLANH2176)

5. **Campaign Context Missing**: Doesn't account for:
   - Spending levels
   - Scandal/controversy
   - Debate performance
   - Opponent quality

---

## Future Enhancements

### 1. Add Demographic Overlays
- Merge with Census data (race, education, income, age)
- Calculate demographic-based expected performance
- Identify demographic groups where candidate over/underperforms

### 2. Temporal Trends
- Track district-level swings over multiple cycles
- Identify trending districts (moving toward D or R)
- Predict future competitiveness

### 3. Machine Learning Predictions
- Train model on 2018-2022 to predict 2024
- Feature engineering: demographics, partisan lean, candidate attributes
- Ensemble methods for robust predictions

### 4. Campaign Finance Integration
- Add spending data by district
- Calculate ROI (votes per dollar spent)
- Identify efficient vs. inefficient districts

### 5. Real-Time Updates
- Integrate with polling data
- Update strength scores as new data arrives
- Early warning system for incumbent vulnerability

---

## Key Takeaways

### For 2024 Texas Races

1. **Allred was the stronger candidate** - Cruz won due to environment, not personal strength
2. **Cruz remains vulnerable** - Consistently underperforms party baseline
3. **O'Rourke peaked in 2018** - Lost crossover appeal by 2022
4. **Environment matters more than candidate** - Trump +12 nationally helped all Rs

### For Future Analysis

1. **Strength scores identify candidate quality** independent of results
2. **vs. Top-of-Ticket is critical metric** - Shows personal vote
3. **Crossover appeal predicts statewide viability** - Must win persuadable voters
4. **Consistency matters** - Candidates with low variance are more predictable

### Strategic Applications

1. **Recruitment**: Use model to identify districts for strong candidates
2. **Resource Allocation**: Invest in districts where candidate has unique appeal
3. **Opposition Research**: Identify opponent weaknesses in specific geographies
4. **Messaging**: Target persuadable districts with crossover-friendly messages

---

## Files

- **Main Model**: `candidate_strength_model.py`
- **Usage**: `python candidate_strength_model.py` to run full analysis
- **Data Required**: District-level election results (house/senate/congressional)

---

**Model Version**: 1.0
**Last Updated**: 2025-01-15
**Author**: Election Analysis Project
