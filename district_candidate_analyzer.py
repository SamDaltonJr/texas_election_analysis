"""
District Candidate Analyzer

Compares district-level candidates (State House, State Senate) to statewide candidates
in their districts to identify:
- Strong district candidates who outperform statewide candidates
- Potential statewide recruitment targets
- Districts where local candidates have unique appeal
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from typing import Dict, List

class DistrictCandidateAnalyzer:
    """Analyze district candidates vs. statewide candidates"""

    def __init__(self):
        """Initialize analyzer with both district races and statewide data"""
        # Load district races (actual State House/Senate elections)
        self.house_races = pd.read_csv('texas_election_data/pdf_extracts/2024_house_races.csv')
        self.senate_races = pd.read_csv('texas_election_data/pdf_extracts/2024_senate_races.csv')

        # Load statewide races broken down by district
        self.statewide_by_house = pd.read_csv('texas_election_data/pdf_extracts/2024_house_district_results.csv')
        self.statewide_by_senate = pd.read_csv('texas_election_data/pdf_extracts/2024_senate_results.csv')

        print(f"Loaded {len(self.house_races)} House race records")
        print(f"Loaded {len(self.senate_races)} Senate race records")
        print(f"Loaded {len(self.statewide_by_house)} statewide results by House district")
        print(f"Loaded {len(self.statewide_by_senate)} statewide results by Senate district")

    def calculate_vs_top_ticket(self, district_level='house', year=2024):
        """
        Calculate how district candidates performed vs. top-of-ticket in their districts

        Returns DataFrame with:
        - District candidate info
        - Top-of-ticket performance in that district
        - Overperformance/underperformance
        """
        if district_level == 'house':
            district_races = self.house_races[self.house_races['year'] == year].copy()
            statewide_data = self.statewide_by_house[
                (self.statewide_by_house['year'] == year) &
                (self.statewide_by_house['district'] != 'STATE')
            ].copy()
            top_office = 'President'  # 2024 is presidential year
        else:
            district_races = self.senate_races[self.senate_races['year'] == year].copy()
            statewide_data = self.statewide_by_senate[
                (self.statewide_by_senate['year'] == year) &
                (self.statewide_by_senate['district'] != 'STATE')
            ].copy()
            top_office = 'President'

        # Get top-of-ticket results
        top_ticket = statewide_data[statewide_data['office'] == top_office].copy()

        # Ensure districts are strings for merging
        district_races['district'] = district_races['district'].astype(str)
        top_ticket['district'] = top_ticket['district'].astype(str)

        results = []

        for _, race_row in district_races.iterrows():
            district = race_row['district']
            candidate = race_row['candidate']
            party = race_row['party']
            votes = race_row['votes']
            pct = race_row['percentage']

            # Get top-ticket performance for this party in this district
            top_ticket_dist = top_ticket[
                (top_ticket['district'] == district) &
                (top_ticket['party'] == party)
            ]

            if not top_ticket_dist.empty:
                top_ticket_pct = top_ticket_dist['percentage'].values[0]
                top_ticket_candidate = top_ticket_dist['candidate'].values[0]
                vs_top_ticket = pct - top_ticket_pct

                # Calculate district partisan lean (D-R margin in presidential race)
                district_top = top_ticket[top_ticket['district'] == district]
                dem_pct = district_top[district_top['party'] == 'D']['percentage'].sum()
                rep_pct = district_top[district_top['party'] == 'R']['percentage'].sum()
                partisan_lean = dem_pct - rep_pct  # Positive = D-leaning, Negative = R-leaning

                # Determine if district leans toward or away from candidate's party
                if party == 'D':
                    favorable_district = partisan_lean > 0
                elif party == 'R':
                    favorable_district = partisan_lean < 0
                else:
                    favorable_district = None

                results.append({
                    'district': district,
                    'district_type': district_level,
                    'candidate': candidate,
                    'party': party,
                    'votes': votes,
                    'percentage': pct,
                    'top_ticket_candidate': top_ticket_candidate,
                    'top_ticket_pct': top_ticket_pct,
                    'vs_top_ticket': vs_top_ticket,
                    'partisan_lean': partisan_lean,
                    'partisan_lean_strength': abs(partisan_lean),
                    'favorable_district': favorable_district
                })

        return pd.DataFrame(results)

    def identify_strong_candidates(self, district_level='house', min_vs_top_ticket=2.0,
                                   party=None):
        """
        Identify strong district candidates who significantly outperformed top-of-ticket

        Parameters:
        - district_level: 'house' or 'senate'
        - min_vs_top_ticket: Minimum outperformance (percentage points)
        - party: Filter by party ('D', 'R', or None for both)

        Returns: DataFrame of strong candidates sorted by vs_top_ticket
        """
        df = self.calculate_vs_top_ticket(district_level=district_level)

        # Filter by party if specified
        if party:
            df = df[df['party'] == party]

        # Filter by minimum outperformance
        strong = df[df['vs_top_ticket'] >= min_vs_top_ticket].copy()

        # Sort by overperformance
        strong = strong.sort_values('vs_top_ticket', ascending=False)

        return strong

    def identify_crossover_appeal_candidates(self, district_level='house', party=None):
        """
        Identify candidates who won or performed well in unfavorable districts

        These candidates have crossover appeal and could be strong statewide prospects
        """
        df = self.calculate_vs_top_ticket(district_level=district_level)

        # Filter by party if specified
        if party:
            df = df[df['party'] == party]

        # Get candidates who won (>50%) in unfavorable districts
        # OR who lost but significantly outperformed top-of-ticket in unfavorable districts
        crossover = df[
            (df['favorable_district'] == False) &
            ((df['percentage'] > 50) | (df['vs_top_ticket'] > 5))
        ].copy()

        # Sort by partisan lean strength (harder districts first) then by vs_top_ticket
        crossover = crossover.sort_values(['partisan_lean_strength', 'vs_top_ticket'],
                                          ascending=[False, False])

        return crossover

    def compare_to_statewide_candidate(self, statewide_candidate, district_level='house'):
        """
        Compare how district candidates performed relative to a specific statewide candidate

        Example: "Show me all State House candidates who outperformed Cruz in their districts"
        """
        df = self.calculate_vs_top_ticket(district_level=district_level)

        # Filter to same party as statewide candidate
        # For now, we'll get the results for both parties and let user filter
        return df.sort_values('vs_top_ticket', ascending=False)

    def generate_recruitment_report(self, party, district_level='house'):
        """
        Generate a report of potential statewide recruitment targets

        Looks for candidates who:
        1. Won their district race
        2. Outperformed top-of-ticket significantly
        3. Showed crossover appeal in competitive/unfavorable districts
        """
        df = self.calculate_vs_top_ticket(district_level=district_level)

        # Filter by party
        df = df[df['party'] == party].copy()

        # Score candidates
        # For unfavorable terrain: if D candidate, negative partisan_lean is unfavorable (R-leaning)
        # if R candidate, positive partisan_lean is unfavorable (D-leaning)
        if party == 'D':
            terrain_score = np.where(df['partisan_lean'] < 0, df['partisan_lean_strength'], -df['partisan_lean'])
        else:
            terrain_score = np.where(df['partisan_lean'] > 0, df['partisan_lean_strength'], df['partisan_lean'])

        df['recruitment_score'] = (
            (df['vs_top_ticket'] * 0.4) +  # Overperformance vs top ticket
            ((df['percentage'] - 50) * 0.3) +  # Margin of victory
            (terrain_score * 0.3)  # Performance in unfavorable terrain
        )

        # Filter to winners only
        winners = df[df['percentage'] > 50].copy()

        # Sort by recruitment score
        winners = winners.sort_values('recruitment_score', ascending=False)

        return winners[[
            'district', 'candidate', 'percentage', 'top_ticket_pct',
            'vs_top_ticket', 'partisan_lean', 'recruitment_score'
        ]]


def main():
    print("="*80)
    print("DISTRICT CANDIDATE ANALYSIS - 2024")
    print("="*80)

    analyzer = DistrictCandidateAnalyzer()

    # Example 1: Strong State House Democrats
    print("\n" + "="*80)
    print("TOP 10 STATE HOUSE DEMOCRATS (Outperformed Harris)")
    print("="*80)
    strong_d = analyzer.identify_strong_candidates(district_level='house', party='D',
                                                    min_vs_top_ticket=2.0)
    print(strong_d[[
        'district', 'candidate', 'percentage', 'top_ticket_pct', 'vs_top_ticket',
        'partisan_lean'
    ]].head(10).to_string(index=False))

    # Example 2: Strong State House Republicans
    print("\n" + "="*80)
    print("TOP 10 STATE HOUSE REPUBLICANS (Outperformed Trump)")
    print("="*80)
    strong_r = analyzer.identify_strong_candidates(district_level='house', party='R',
                                                    min_vs_top_ticket=2.0)
    print(strong_r[[
        'district', 'candidate', 'percentage', 'top_ticket_pct', 'vs_top_ticket',
        'partisan_lean'
    ]].head(10).to_string(index=False))

    # Example 3: Crossover Appeal - Democrats who won/performed in R districts
    print("\n" + "="*80)
    print("DEMOCRATS WITH CROSSOVER APPEAL (Won or performed well in R-leaning districts)")
    print("="*80)
    crossover_d = analyzer.identify_crossover_appeal_candidates(district_level='house',
                                                                 party='D')
    print(crossover_d[[
        'district', 'candidate', 'percentage', 'top_ticket_pct', 'vs_top_ticket',
        'partisan_lean'
    ]].head(10).to_string(index=False))

    # Example 4: Recruitment Report
    print("\n" + "="*80)
    print("DEMOCRATIC RECRUITMENT TARGETS (State House)")
    print("="*80)
    recruitment = analyzer.generate_recruitment_report(party='D', district_level='house')
    print(recruitment.head(15).to_string(index=False))

    # Example 5: State Senate Analysis
    print("\n" + "="*80)
    print("STATE SENATE ANALYSIS")
    print("="*80)
    senate_results = analyzer.calculate_vs_top_ticket(district_level='senate')
    print(senate_results[[
        'district', 'candidate', 'party', 'percentage', 'top_ticket_pct',
        'vs_top_ticket', 'partisan_lean'
    ]].sort_values('vs_top_ticket', ascending=False).to_string(index=False))

if __name__ == "__main__":
    main()
