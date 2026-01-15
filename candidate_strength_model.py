"""
Candidate Strength Analysis Model

Analyzes individual candidate strength by comparing district-level performance
to statewide baseline results, accounting for:
- Partisan baseline (district lean)
- National/statewide political environment
- Incumbency advantage
- Ticket performance comparison

Key Metrics:
1. Candidate Over/Underperformance: How much better/worse than party baseline
2. Relative Strength Score: Performance relative to top-of-ticket race
3. Geographic Strength: Where candidates do better/worse than expected
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class CandidateStrengthAnalyzer:
    """Analyze candidate strength across districts"""

    def __init__(self, geographic_level='house'):
        """
        Initialize analyzer

        Parameters:
        - geographic_level: 'house', 'senate', or 'congressional'
        """
        self.geographic_level = geographic_level
        self.data = None
        self.baseline_data = None

        # Load appropriate dataset
        file_map = {
            'house': 'texas_election_data/pdf_extracts/2018_2024_house_district_results_all.csv',
            'senate': 'texas_election_data/pdf_extracts/2018_2024_senate_results_combined.csv',
            'congressional': 'texas_election_data/pdf_extracts/2018_2024_congressional_results_combined.csv'
        }

        self.data = pd.read_csv(file_map[geographic_level])

        # Incumbency data (can be expanded)
        self.incumbents = {
            2018: {'Cruz': True, 'Abbott': True, 'Patrick': True, 'Paxton': True},
            2020: {'Trump': True, 'Cornyn': True},
            2022: {'Abbott': True, 'Patrick': True, 'Paxton': True},
            2024: {'Trump': True, 'Cruz': True}
        }

    def calculate_district_partisan_lean(self, year: int,
                                         baseline_race: str = None,
                                         baseline_year: int = None) -> pd.DataFrame:
        """
        Calculate partisan lean of each district based on a baseline race

        Uses presidential results as baseline for partisan lean
        """
        if baseline_year is None:
            # Use most recent presidential election before or at the target year
            if year >= 2024:
                baseline_year = 2024
                baseline_race = 'President'
            elif year >= 2020:
                baseline_year = 2020
                baseline_race = 'President'
            elif year >= 2018:
                # For 2018-2019, use 2016 presidential (not in our data, so use Governor)
                baseline_year = 2018
                baseline_race = 'Governor'
            else:
                baseline_year = 2016
                baseline_race = 'President'

        # If baseline_race not specified, default based on year
        if baseline_race is None:
            baseline_race = 'President' if year in [2020, 2024] else 'Governor'

        # Get baseline race results
        baseline = self.data[
            (self.data['year'] == baseline_year) &
            (self.data['office'] == baseline_race) &
            (self.data['district'] != 'STATE')
        ].copy()

        # If still no data, return empty DataFrame
        if baseline.empty:
            return pd.DataFrame(columns=['district', 'baseline_year', 'baseline_race',
                                        'dem_pct', 'rep_pct', 'dem_margin',
                                        'partisan_lean', 'lean_strength'])

        # Calculate D vs R margin
        district_margins = []

        for district in baseline['district'].unique():
            dist_data = baseline[baseline['district'] == district]

            dem_votes = dist_data[dist_data['party'] == 'D']['votes'].sum()
            rep_votes = dist_data[dist_data['party'] == 'R']['votes'].sum()
            total_votes = dem_votes + rep_votes

            if total_votes > 0:
                dem_pct = dem_votes / total_votes * 100
                rep_pct = rep_votes / total_votes * 100
                margin = dem_pct - rep_pct  # Positive = more Democratic

                district_margins.append({
                    'district': district,
                    'baseline_year': baseline_year,
                    'baseline_race': baseline_race,
                    'dem_pct': dem_pct,
                    'rep_pct': rep_pct,
                    'dem_margin': margin,
                    'partisan_lean': 'D' if margin > 0 else 'R',
                    'lean_strength': abs(margin)
                })

        return pd.DataFrame(district_margins)

    def calculate_candidate_performance(self, year: int, office: str,
                                       candidate: str) -> pd.DataFrame:
        """
        Calculate how a candidate performed relative to baseline expectations
        """
        # Get candidate's results
        cand_results = self.data[
            (self.data['year'] == year) &
            (self.data['office'] == office) &
            (self.data['candidate'] == candidate) &
            (self.data['district'] != 'STATE')
        ].copy()

        if cand_results.empty:
            return pd.DataFrame()

        # Get statewide result for this candidate
        statewide = self.data[
            (self.data['year'] == year) &
            (self.data['office'] == office) &
            (self.data['candidate'] == candidate) &
            (self.data['district'] == 'STATE')
        ]

        statewide_pct = statewide['percentage'].values[0] if not statewide.empty else None

        # Get partisan lean for each district
        partisan_lean = self.calculate_district_partisan_lean(year)

        # Merge with candidate results
        if not partisan_lean.empty:
            analysis = cand_results.merge(
                partisan_lean[['district', 'dem_margin', 'partisan_lean', 'lean_strength']],
                on='district',
                how='left'
            )
        else:
            # No partisan lean data available, add empty columns
            analysis = cand_results.copy()
            analysis['dem_margin'] = 0
            analysis['partisan_lean'] = 'R'
            analysis['lean_strength'] = 0

        # Calculate over/underperformance
        if statewide_pct:
            analysis['vs_statewide'] = analysis['percentage'] - statewide_pct
        else:
            analysis['vs_statewide'] = 0

        # Get top-of-ticket comparison (Presidential or Gubernatorial)
        if year in [2020, 2024] and office != 'President':
            # Compare to President
            top_ticket = self.get_party_performance(year, 'President',
                                                    cand_results['party'].values[0])
            analysis = analysis.merge(
                top_ticket[['district', 'percentage']].rename(
                    columns={'percentage': 'top_ticket_pct'}
                ),
                on='district',
                how='left'
            )
            analysis['vs_top_ticket'] = analysis['percentage'] - analysis['top_ticket_pct']
            analysis['top_ticket_race'] = 'President'

        elif year in [2018, 2022] and office != 'Governor':
            # Compare to Governor
            top_ticket = self.get_party_performance(year, 'Governor',
                                                    cand_results['party'].values[0])
            analysis = analysis.merge(
                top_ticket[['district', 'percentage']].rename(
                    columns={'percentage': 'top_ticket_pct'}
                ),
                on='district',
                how='left'
            )
            analysis['vs_top_ticket'] = analysis['percentage'] - analysis['top_ticket_pct']
            analysis['top_ticket_race'] = 'Governor'
        else:
            analysis['top_ticket_pct'] = None
            analysis['vs_top_ticket'] = 0
            analysis['top_ticket_race'] = None

        # Add incumbency indicator
        analysis['is_incumbent'] = candidate in self.incumbents.get(year, {})

        return analysis

    def get_party_performance(self, year: int, office: str, party: str) -> pd.DataFrame:
        """Get party's performance in a specific race"""
        return self.data[
            (self.data['year'] == year) &
            (self.data['office'] == office) &
            (self.data['party'] == party) &
            (self.data['district'] != 'STATE')
        ][['district', 'candidate', 'percentage']].copy()

    def calculate_strength_score(self, candidate_analysis: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate overall candidate strength score

        Components:
        1. Statewide performance (how well they did overall)
        2. District overperformance (beat baseline in tough districts)
        3. Geographic breadth (performed well across diverse districts)
        4. Top-ticket differential (personal vote beyond party)
        """
        if candidate_analysis.empty:
            return pd.DataFrame()

        # Add weighted strength score
        # Positive score = strong candidate, Negative = weak candidate

        # Weight overperformance in unfavorable districts more heavily
        candidate_analysis['weighted_overperformance'] = np.where(
            candidate_analysis['partisan_lean'] != candidate_analysis['party'],
            candidate_analysis['vs_statewide'] * 2,  # 2x weight in opposite-leaning districts
            candidate_analysis['vs_statewide']
        )

        # Calculate strength score components
        summary = {
            'candidate': candidate_analysis['candidate'].values[0],
            'year': candidate_analysis['year'].values[0],
            'office': candidate_analysis['office'].values[0],
            'party': candidate_analysis['party'].values[0],
            'is_incumbent': candidate_analysis['is_incumbent'].values[0],

            # Performance metrics
            'statewide_pct': candidate_analysis['percentage'].mean(),  # Should match statewide
            'avg_vs_statewide': candidate_analysis['vs_statewide'].mean(),
            'avg_vs_top_ticket': candidate_analysis['vs_top_ticket'].mean(),

            # Geographic strength
            'districts_won': (candidate_analysis['percentage'] > 50).sum(),
            'districts_total': len(candidate_analysis),
            'win_rate': (candidate_analysis['percentage'] > 50).sum() / len(candidate_analysis),

            # Overperformance in challenging districts
            'avg_overperf_opposite_districts': candidate_analysis[
                candidate_analysis['partisan_lean'] != candidate_analysis['party']
            ]['vs_statewide'].mean(),

            'avg_overperf_favorable_districts': candidate_analysis[
                candidate_analysis['partisan_lean'] == candidate_analysis['party']
            ]['vs_statewide'].mean(),

            # Consistency
            'std_dev_performance': candidate_analysis['vs_statewide'].std(),

            # Overall strength score (composite)
            'overall_strength_score': (
                candidate_analysis['weighted_overperformance'].mean() * 0.4 +
                candidate_analysis['vs_top_ticket'].mean() * 0.3 +
                (candidate_analysis['percentage'].mean() - 50) * 0.2 +
                -(candidate_analysis['vs_statewide'].std() * 0.1)  # Lower std dev = more consistent
            )
        }

        return pd.DataFrame([summary])

    def analyze_race(self, year: int, office: str) -> pd.DataFrame:
        """Analyze all candidates in a specific race"""

        candidates = self.data[
            (self.data['year'] == year) &
            (self.data['office'] == office) &
            (self.data['district'] == 'STATE')
        ]['candidate'].unique()

        all_scores = []

        for candidate in candidates:
            perf = self.calculate_candidate_performance(year, office, candidate)
            if not perf.empty:
                score = self.calculate_strength_score(perf)
                all_scores.append(score)

        if all_scores:
            return pd.concat(all_scores, ignore_index=True).sort_values(
                'overall_strength_score', ascending=False
            )
        else:
            return pd.DataFrame()

    def compare_candidates_across_elections(self, candidate: str) -> pd.DataFrame:
        """
        Track a single candidate's performance across multiple elections
        e.g., Cruz 2018 vs 2024, O'Rourke 2018 vs 2022
        """
        candidate_races = self.data[
            (self.data['candidate'] == candidate) &
            (self.data['district'] == 'STATE')
        ][['year', 'office']].drop_duplicates()

        all_analyses = []

        for _, race in candidate_races.iterrows():
            perf = self.calculate_candidate_performance(race['year'], race['office'], candidate)
            if not perf.empty:
                score = self.calculate_strength_score(perf)
                all_analyses.append(score)

        if all_analyses:
            return pd.concat(all_analyses, ignore_index=True).sort_values('year')
        else:
            return pd.DataFrame()


def main():
    print("="*80)
    print("TEXAS CANDIDATE STRENGTH ANALYSIS")
    print("="*80)

    # Analyze at State House district level (most granular)
    analyzer = CandidateStrengthAnalyzer(geographic_level='house')

    print("\n" + "="*80)
    print("2024 PRESIDENTIAL RACE - Candidate Strength Analysis")
    print("="*80)

    pres_2024 = analyzer.analyze_race(2024, 'President')
    print(pres_2024[[
        'candidate', 'party', 'statewide_pct', 'overall_strength_score',
        'avg_vs_top_ticket', 'win_rate', 'std_dev_performance'
    ]].to_string(index=False))

    print("\n" + "="*80)
    print("2024 U.S. SENATE RACE - Candidate Strength Analysis")
    print("="*80)

    senate_2024 = analyzer.analyze_race(2024, 'U.S. Senate')
    print(senate_2024[[
        'candidate', 'party', 'is_incumbent', 'statewide_pct',
        'overall_strength_score', 'avg_vs_top_ticket',
        'avg_overperf_opposite_districts', 'win_rate'
    ]].to_string(index=False))

    print("\n" + "="*80)
    print("TED CRUZ - Performance Across Elections (2018 vs 2024)")
    print("="*80)

    cruz_history = analyzer.compare_candidates_across_elections('Cruz')
    print(cruz_history[[
        'year', 'office', 'statewide_pct', 'overall_strength_score',
        'avg_vs_top_ticket', 'win_rate', 'districts_won'
    ]].to_string(index=False))

    print("\n" + "="*80)
    print("BETO O'ROURKE - Performance Across Elections (2018 vs 2022)")
    print("="*80)

    beto_history = analyzer.compare_candidates_across_elections("O'Rourke")
    print(beto_history[[
        'year', 'office', 'statewide_pct', 'overall_strength_score',
        'avg_vs_top_ticket', 'win_rate', 'districts_won'
    ]].to_string(index=False))

    print("\n" + "="*80)
    print("2024 SENATE: CRUZ VS ALLRED - District-Level Comparison")
    print("="*80)

    # Get detailed district performance for both candidates
    cruz_detailed = analyzer.calculate_candidate_performance(2024, 'U.S. Senate', 'Cruz')
    allred_detailed = analyzer.calculate_candidate_performance(2024, 'U.S. Senate', 'Allred')

    # Show top 10 districts where each candidate overperformed
    print("\nCruz's Top 10 Overperforming Districts:")
    cruz_top = cruz_detailed.nlargest(10, 'vs_top_ticket')[
        ['district', 'percentage', 'vs_statewide', 'vs_top_ticket', 'partisan_lean']
    ]
    print(cruz_top.to_string(index=False))

    print("\nAllred's Top 10 Overperforming Districts:")
    allred_top = allred_detailed.nlargest(10, 'vs_top_ticket')[
        ['district', 'percentage', 'vs_statewide', 'vs_top_ticket', 'partisan_lean']
    ]
    print(allred_top.to_string(index=False))

    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    print("""
Strength Score Interpretation:
- Positive score: Strong candidate, performed better than baseline
- Negative score: Weak candidate, performed worse than baseline
- Higher absolute value: Stronger personal brand (positive or negative)

vs_top_ticket: How much better/worse than Presidential/Gubernatorial candidate
- Positive: Outperformed top of ticket (strong personal vote)
- Negative: Underperformed top of ticket (weak personal vote)

Overperformance in opposite districts: Key indicator of crossover appeal
- Shows ability to win persuadable voters
- Critical for statewide success in competitive states
    """)

if __name__ == "__main__":
    main()
