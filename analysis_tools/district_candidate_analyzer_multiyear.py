"""
Multi-Year District Candidate Analyzer

Compares district-level candidates to statewide candidates across 2018-2024,
with flags for race competitiveness (contested, major party opposition, etc.)
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from typing import Dict, List

class MultiYearDistrictCandidateAnalyzer:
    """Analyze district candidates vs. statewide candidates across multiple years"""

    def __init__(self):
        """Initialize analyzer with all years of data"""
        # Load district races (actual State House/Senate elections)
        self.house_races_2024 = pd.read_csv('texas_election_data/pdf_extracts/2024_house_races.csv')
        self.house_races_2018_2022 = pd.read_csv('texas_election_data/pdf_extracts/2018_2022_house_races.csv')
        self.house_races = pd.concat([self.house_races_2018_2022, self.house_races_2024], ignore_index=True)

        self.senate_races_2024 = pd.read_csv('texas_election_data/pdf_extracts/2024_senate_races.csv')
        self.senate_races_2018_2022 = pd.read_csv('texas_election_data/pdf_extracts/2018_2022_senate_races.csv')
        self.senate_races = pd.concat([self.senate_races_2018_2022, self.senate_races_2024], ignore_index=True)

        # Load congressional races (U.S. House)
        self.congressional_races = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_congressional_races.csv')

        # Load statewide races broken down by district
        self.statewide_by_house = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_house_district_results_all.csv')

        # Load statewide by Senate (use CORRECT file if available)
        import os
        self.statewide_by_senate = None
        if os.path.exists('texas_election_data/pdf_extracts/2018_2024_senate_results_combined_CORRECT.csv'):
            self.statewide_by_senate = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_senate_results_combined_CORRECT.csv')
        elif os.path.exists('texas_election_data/pdf_extracts/2018_2024_senate_results_combined.csv'):
            self.statewide_by_senate = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_senate_results_combined.csv')

        # Congressional statewide data currently unavailable (incorrect source data)
        self.statewide_by_congressional = None
        try:
            if os.path.exists('texas_election_data/pdf_extracts/2018_2024_congressional_results_combined.csv'):
                self.statewide_by_congressional = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_congressional_results_combined.csv')
        except:
            pass

        print(f"Loaded {len(self.house_races)} House race records ({len(self.house_races['year'].unique())} years)")
        print(f"Loaded {len(self.senate_races)} Senate race records ({len(self.senate_races['year'].unique())} years)")
        print(f"Loaded {len(self.congressional_races)} Congressional race records ({len(self.congressional_races['year'].unique())} years)")
        if self.statewide_by_senate is None:
            print("⚠ Senate statewide data unavailable - vs_top_ticket analysis disabled for senate races")
        else:
            print(f"✓ Senate statewide data loaded ({len(self.statewide_by_senate)} records, {len(self.statewide_by_senate['year'].unique())} years)")
        if self.statewide_by_congressional is None:
            print("⚠ Congressional statewide data unavailable - vs_top_ticket analysis disabled for congressional races")
        print(f"Years available: {sorted(self.house_races['year'].unique())}")

    def classify_race_competitiveness(self, district_races_for_office):
        """
        Classify each race by competitiveness

        Returns DataFrame with added columns:
        - has_major_party_opponent: Both D and R candidates present
        - is_contested: More than one candidate
        - is_competitive: Winning margin < 20 points
        - opposition_strength: 'strong', 'moderate', 'weak', or 'none'
        """
        results = []

        for (district, year), group in district_races_for_office.groupby(['district', 'year']):
            candidates = group.to_dict('records')

            # Check for major party presence
            parties = set(group['party'].tolist())
            has_d = 'D' in parties
            has_r = 'R' in parties
            has_major_party_opponent = has_d and has_r

            # Check if contested
            is_contested = len(candidates) > 1

            # Get winning percentage
            winning_pct = group['percentage'].max()

            # Check if competitive (winning margin < 20 points)
            if len(candidates) >= 2:
                top_two = group.nlargest(2, 'percentage')['percentage'].tolist()
                margin = top_two[0] - top_two[1]
                is_competitive = margin < 20
            else:
                margin = 100
                is_competitive = False

            # Classify opposition strength
            if not is_contested:
                opposition_strength = 'none'
            elif not has_major_party_opponent:
                opposition_strength = 'weak'  # Third party only
            elif margin < 10:
                opposition_strength = 'strong'
            elif margin < 20:
                opposition_strength = 'moderate'
            else:
                opposition_strength = 'weak'

            # Add classification to each candidate in this race
            for candidate in candidates:
                candidate['has_major_party_opponent'] = has_major_party_opponent
                candidate['is_contested'] = is_contested
                candidate['is_competitive'] = is_competitive
                candidate['winning_margin'] = margin
                candidate['opposition_strength'] = opposition_strength
                results.append(candidate)

        return pd.DataFrame(results)

    def calculate_vs_top_ticket(self, district_level='house', year=None):
        """
        Calculate how district candidates performed vs. top-of-ticket in their districts

        Parameters:
        - district_level: 'house', 'senate', or 'congressional'
        - year: Specific year, or None for all years

        Returns DataFrame with competitiveness flags
        """
        if district_level == 'house':
            district_races = self.house_races.copy()
            statewide_data = self.statewide_by_house.copy()
        elif district_level == 'senate':
            if self.statewide_by_senate is None:
                raise ValueError("Senate statewide data is not available. vs_top_ticket analysis cannot be performed for senate races.")
            district_races = self.senate_races.copy()
            statewide_data = self.statewide_by_senate.copy()
        else:  # congressional
            if self.statewide_by_congressional is None:
                raise ValueError("Congressional statewide data is not available. vs_top_ticket analysis cannot be performed for congressional races.")
            district_races = self.congressional_races.copy()
            statewide_data = self.statewide_by_congressional.copy()

        # Filter by year if specified
        if year:
            district_races = district_races[district_races['year'] == year]
            statewide_data = statewide_data[statewide_data['year'] == year]

        # Classify race competitiveness
        district_races = self.classify_race_competitiveness(district_races)

        # Filter statewide to non-STATE districts
        statewide_data = statewide_data[statewide_data['district'] != 'STATE'].copy()

        # Ensure districts are strings for merging
        district_races['district'] = district_races['district'].astype(str)
        statewide_data['district'] = statewide_data['district'].astype(str)

        results = []

        for _, race_row in district_races.iterrows():
            district = race_row['district']
            year = race_row['year']
            candidate = race_row['candidate']
            party = race_row['party']
            votes = race_row['votes']
            pct = race_row['percentage']

            # Get top-of-ticket office for this year
            if year in [2024, 2020]:
                top_office = 'President'
            elif year in [2022, 2018]:
                top_office = 'Governor'
            else:
                continue  # Skip if we don't have a top-of-ticket race

            # Get top-ticket performance for this party in this district
            top_ticket_dist = statewide_data[
                (statewide_data['district'] == district) &
                (statewide_data['year'] == year) &
                (statewide_data['office'] == top_office) &
                (statewide_data['party'] == party)
            ]

            if not top_ticket_dist.empty:
                top_ticket_pct = top_ticket_dist['percentage'].values[0]
                top_ticket_candidate = top_ticket_dist['candidate'].values[0]
                vs_top_ticket = pct - top_ticket_pct

                # Calculate district partisan lean
                district_top = statewide_data[
                    (statewide_data['district'] == district) &
                    (statewide_data['year'] == year) &
                    (statewide_data['office'] == top_office)
                ]
                dem_pct = district_top[district_top['party'] == 'D']['percentage'].sum()
                rep_pct = district_top[district_top['party'] == 'R']['percentage'].sum()
                partisan_lean = dem_pct - rep_pct

                # Determine if district is favorable
                if party == 'D':
                    favorable_district = partisan_lean > 0
                elif party == 'R':
                    favorable_district = partisan_lean < 0
                else:
                    favorable_district = None

                results.append({
                    'year': year,
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
                    'favorable_district': favorable_district,
                    # Competitiveness flags
                    'has_major_party_opponent': race_row['has_major_party_opponent'],
                    'is_contested': race_row['is_contested'],
                    'is_competitive': race_row['is_competitive'],
                    'winning_margin': race_row['winning_margin'],
                    'opposition_strength': race_row['opposition_strength']
                })

        return pd.DataFrame(results)

    def identify_strong_candidates(self, district_level='house', year=None,
                                   min_vs_top_ticket=2.0, party=None,
                                   require_major_party_opponent=True,
                                   require_contested=True):
        """
        Identify strong district candidates with filters for race quality

        Parameters:
        - district_level: 'house' or 'senate'
        - year: Specific year or None for all years
        - min_vs_top_ticket: Minimum outperformance (percentage points)
        - party: Filter by party ('D', 'R', or None)
        - require_major_party_opponent: Only include races with both D and R
        - require_contested: Only include contested races
        """
        df = self.calculate_vs_top_ticket(district_level=district_level, year=year)

        # Apply competitiveness filters
        if require_major_party_opponent:
            df = df[df['has_major_party_opponent'] == True]

        if require_contested:
            df = df[df['is_contested'] == True]

        # Filter by party if specified
        if party:
            df = df[df['party'] == party]

        # Filter by minimum outperformance
        strong = df[df['vs_top_ticket'] >= min_vs_top_ticket].copy()

        # Sort by overperformance
        strong = strong.sort_values('vs_top_ticket', ascending=False)

        return strong

    def identify_crossover_appeal_candidates(self, district_level='house', year=None,
                                            party=None, require_major_party_opponent=True):
        """
        Identify candidates who won or performed well in unfavorable districts

        Only includes candidates who faced real opposition
        """
        df = self.calculate_vs_top_ticket(district_level=district_level, year=year)

        # Apply competitiveness filter
        if require_major_party_opponent:
            df = df[df['has_major_party_opponent'] == True]

        # Filter by party if specified
        if party:
            df = df[df['party'] == party]

        # Get candidates in unfavorable districts who won or outperformed significantly
        crossover = df[
            (df['favorable_district'] == False) &
            ((df['percentage'] > 50) | (df['vs_top_ticket'] > 5))
        ].copy()

        # Sort by partisan lean strength then vs_top_ticket
        crossover = crossover.sort_values(['partisan_lean_strength', 'vs_top_ticket'],
                                          ascending=[False, False])

        return crossover

    def track_candidate_over_time(self, candidate_name, district_level='house'):
        """
        Track a specific candidate's performance across multiple elections

        Parameters:
        - candidate_name: Candidate's name (partial match OK)
        - district_level: 'house' or 'senate'
        """
        df = self.calculate_vs_top_ticket(district_level=district_level)

        # Find candidates matching name
        matches = df[df['candidate'].str.contains(candidate_name, case=False, na=False)]

        if matches.empty:
            print(f"No candidates found matching '{candidate_name}'")
            return pd.DataFrame()

        # Sort by year
        matches = matches.sort_values('year')

        return matches[[
            'year', 'district', 'candidate', 'party', 'percentage',
            'top_ticket_candidate', 'top_ticket_pct', 'vs_top_ticket',
            'partisan_lean', 'has_major_party_opponent', 'opposition_strength',
            'winning_margin'
        ]]

    def compare_years(self, year1, year2, district_level='house', party=None):
        """
        Compare candidate performance between two years

        Useful for seeing trends: which districts improved/declined for a party
        """
        df = self.calculate_vs_top_ticket(district_level=district_level)

        if party:
            df = df[df['party'] == party]

        # Get data for both years
        year1_data = df[df['year'] == year1].copy()
        year2_data = df[df['year'] == year2].copy()

        # Merge on district to compare
        comparison = year1_data.merge(
            year2_data,
            on=['district', 'party'],
            suffixes=(f'_{year1}', f'_{year2}')
        )

        # Calculate changes
        comparison['pct_change'] = comparison[f'percentage_{year2}'] - comparison[f'percentage_{year1}']
        comparison['vs_ticket_change'] = comparison[f'vs_top_ticket_{year2}'] - comparison[f'vs_top_ticket_{year1}']

        return comparison.sort_values('pct_change', ascending=False)


def main():
    print("="*80)
    print("MULTI-YEAR DISTRICT CANDIDATE ANALYSIS")
    print("="*80)

    analyzer = MultiYearDistrictCandidateAnalyzer()

    # Example 1: Strong 2022 House Democrats (with real opposition)
    print("\n" + "="*80)
    print("TOP 10 STATE HOUSE DEMOCRATS - 2022 (Real Opposition Only)")
    print("="*80)
    strong_d_2022 = analyzer.identify_strong_candidates(
        district_level='house',
        year=2022,
        party='D',
        min_vs_top_ticket=2.0,
        require_major_party_opponent=True
    )
    print(strong_d_2022[[
        'district', 'candidate', 'percentage', 'top_ticket_pct', 'vs_top_ticket',
        'opposition_strength', 'winning_margin', 'partisan_lean'
    ]].head(10).to_string(index=False))

    # Example 2: Compare all years for a specific candidate
    print("\n" + "="*80)
    print("CANDIDATE TRAJECTORY: Ted Cruz's District Performance")
    print("(State Senate District races where Cruz also appeared on ballot)")
    print("="*80)

    # Example 3: Strong Democrats across ALL years (with opposition)
    print("\n" + "="*80)
    print("STRONGEST HOUSE DEMOCRATS ACROSS ALL YEARS (Real Opposition)")
    print("="*80)
    strong_all = analyzer.identify_strong_candidates(
        district_level='house',
        party='D',
        min_vs_top_ticket=5.0,
        require_major_party_opponent=True
    )
    print(strong_all[[
        'year', 'district', 'candidate', 'percentage', 'vs_top_ticket',
        'opposition_strength', 'partisan_lean'
    ]].head(15).to_string(index=False))

    # Example 4: Crossover appeal - Democrats in R districts (2022)
    print("\n" + "="*80)
    print("CROSSOVER APPEAL - 2022 DEMOCRATS IN R-LEANING DISTRICTS")
    print("(Major party opposition only)")
    print("="*80)
    crossover_2022 = analyzer.identify_crossover_appeal_candidates(
        district_level='house',
        year=2022,
        party='D',
        require_major_party_opponent=True
    )
    print(crossover_2022[[
        'district', 'candidate', 'percentage', 'vs_top_ticket',
        'partisan_lean', 'opposition_strength', 'winning_margin'
    ]].head(10).to_string(index=False))

    # Example 5: Compare 2018 vs 2022 for Democrats
    print("\n" + "="*80)
    print("DEMOCRAT PERFORMANCE CHANGE: 2018 → 2022")
    print("(Districts with D candidates in both years)")
    print("="*80)
    comparison = analyzer.compare_years(2018, 2022, district_level='house', party='D')
    print(comparison[[
        'district', f'candidate_2018', f'candidate_2022',
        f'percentage_2018', f'percentage_2022', 'pct_change',
        f'vs_top_ticket_2018', f'vs_top_ticket_2022', 'vs_ticket_change'
    ]].head(10).to_string(index=False))

    # Example 6: Track specific candidate
    print("\n" + "="*80)
    print("CANDIDATE TRACKING: Lambert (HD-71)")
    print("="*80)
    lambert = analyzer.track_candidate_over_time('Lambert', district_level='house')
    if not lambert.empty:
        print(lambert.to_string(index=False))

if __name__ == "__main__":
    main()
