"""
Political WAR (Wins Above Replacement) Model

Calculates how much better a candidate performed than a "replacement level"
candidate would have in the same district/environment using regression analysis.

Similar to baseball's WAR, this measures candidate quality independent of
district partisanship and national environment.
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os


class PoliticalWARModel:
    """
    Calculate Political WAR scores using regression analysis

    Model predicts expected vote margin based on:
    - District partisan lean
    - Incumbency status
    - National/statewide environment
    - Opposition quality

    WAR = Actual Margin - Expected Margin
    """

    def __init__(self):
        """Initialize the Political WAR model"""
        self.model = None
        self.feature_importance = None
        self.training_data = None

        # Load district race data
        self._load_data()

        # Calculate incumbency
        self._detect_incumbency()

    def _load_data(self):
        """Load all district race and statewide data"""
        print("Loading election data...")

        # District races (actual races FOR districts)
        house_2018_2022 = pd.read_csv('texas_election_data/pdf_extracts/2018_2022_house_races.csv')
        house_2024 = pd.read_csv('texas_election_data/pdf_extracts/2024_house_races.csv')
        senate_2018_2022 = pd.read_csv('texas_election_data/pdf_extracts/2018_2022_senate_races.csv')
        senate_2024 = pd.read_csv('texas_election_data/pdf_extracts/2024_senate_races.csv')

        # Combine and add district level
        house_2018_2022['district_level'] = 'house'
        house_2024['district_level'] = 'house'
        senate_2018_2022['district_level'] = 'senate'
        senate_2024['district_level'] = 'senate'

        self.district_races = pd.concat([
            house_2018_2022, house_2024,
            senate_2018_2022, senate_2024
        ], ignore_index=True)

        # Statewide races by district
        self.statewide_by_house = pd.read_csv(
            'texas_election_data/pdf_extracts/2018_2024_house_results_combined_CORRECT.csv'
        )
        self.statewide_by_senate = pd.read_csv(
            'texas_election_data/pdf_extracts/2018_2024_senate_results_combined_CORRECT.csv'
        )

        print(f"  Loaded {len(self.district_races):,} district race records")

    def _detect_incumbency(self):
        """
        Detect incumbents by tracking candidates who won in previous cycle

        A candidate is an incumbent if they:
        1. Won the same district in the previous election (2 years ago)
        2. Are running again in the current election
        """
        print("\nDetecting incumbency status...")

        # Sort by year to process chronologically
        self.district_races = self.district_races.sort_values(['district_level', 'district', 'year'])

        # Add incumbency flag
        self.district_races['is_incumbent'] = False

        # Track winners by district
        for district_level in ['house', 'senate']:
            level_races = self.district_races[self.district_races['district_level'] == district_level]

            # Get winners for each district/year
            winners = level_races.loc[level_races.groupby(['district', 'year'])['percentage'].idxmax()]

            # For each election year, check if candidate won 2 years ago
            for year in sorted(level_races['year'].unique()):
                if year == 2018:  # No prior data
                    continue

                prior_year = year - 2

                # Get winners from prior election
                prior_winners = winners[winners['year'] == prior_year]

                # Mark current candidates who won previously as incumbents
                for _, prior_winner in prior_winners.iterrows():
                    mask = (
                        (self.district_races['year'] == year) &
                        (self.district_races['district'] == prior_winner['district']) &
                        (self.district_races['district_level'] == district_level) &
                        (self.district_races['candidate'] == prior_winner['candidate'])
                    )
                    self.district_races.loc[mask, 'is_incumbent'] = True

        incumbent_count = self.district_races['is_incumbent'].sum()
        print(f"  Identified {incumbent_count} incumbent candidates")

    def _get_district_partisan_lean(self, row):
        """
        Get district partisan lean for a given race

        Uses top-of-ticket race (President/Governor/U.S. Senate) to calculate
        D% - R% margin in the district
        """
        year = row['year']
        district = str(row['district'])
        district_level = row['district_level']

        # Select appropriate statewide data
        if district_level == 'house':
            statewide_df = self.statewide_by_house
        elif district_level == 'senate':
            statewide_df = self.statewide_by_senate
        else:
            return None

        # Determine top-of-ticket office
        if district_level == 'senate':
            top_office = 'U.S. Senate'
        elif year in [2024, 2020]:
            top_office = 'President'
        else:
            top_office = 'Governor'

        # Get top-of-ticket results for this district
        district_results = statewide_df[
            (statewide_df['year'] == year) &
            (statewide_df['district'] == district) &
            (statewide_df['office'] == top_office)
        ]

        if len(district_results) == 0:
            return None

        # Calculate D% - R%
        dem_pct = district_results[district_results['party'] == 'D']['percentage'].sum()
        rep_pct = district_results[district_results['party'] == 'R']['percentage'].sum()

        return dem_pct - rep_pct

    def _get_statewide_environment(self, row):
        """
        Get statewide environment (national tide) for this election

        Returns statewide D% - R% margin in top-of-ticket race
        """
        year = row['year']
        district_level = row['district_level']

        # Select appropriate statewide data
        if district_level == 'house':
            statewide_df = self.statewide_by_house
        elif district_level == 'senate':
            statewide_df = self.statewide_by_senate
        else:
            return None

        # Determine top-of-ticket office
        if district_level == 'senate':
            top_office = 'U.S. Senate'
        elif year in [2024, 2020]:
            top_office = 'President'
        else:
            top_office = 'Governor'

        # Get statewide results (district == 'STATE')
        state_results = statewide_df[
            (statewide_df['year'] == year) &
            (statewide_df['district'] == 'STATE') &
            (statewide_df['office'] == top_office)
        ]

        if len(state_results) == 0:
            return None

        # Calculate statewide D% - R%
        dem_pct = state_results[state_results['party'] == 'D']['percentage'].sum()
        rep_pct = state_results[state_results['party'] == 'R']['percentage'].sum()

        return dem_pct - rep_pct

    def prepare_training_data(self):
        """
        Prepare training data with features and target variable

        Features:
        - district_partisan_lean: D% - R% in top-ticket race for this district
        - is_incumbent: 1 if candidate won this district 2 years ago, 0 otherwise
        - statewide_environment: Statewide D% - R% in top-ticket race
        - has_major_opponent: 1 if facing D or R opponent, 0 if only L/I/none
        - is_democrat: 1 if Democrat, 0 if Republican (exclude third parties)

        Target:
        - vote_margin: Candidate's vote % - opponent's vote %
        """
        print("\nPreparing training data...")

        # Only use races with major party candidates (D or R)
        major_party_races = self.district_races[
            self.district_races['party'].isin(['D', 'R'])
        ].copy()

        # Calculate features for each candidate
        features_list = []

        for idx, row in major_party_races.iterrows():
            # Get district partisan lean
            partisan_lean = self._get_district_partisan_lean(row)
            if partisan_lean is None:
                continue

            # Get statewide environment
            environment = self._get_statewide_environment(row)
            if environment is None:
                continue

            # Check for major party opponent
            same_race = major_party_races[
                (major_party_races['year'] == row['year']) &
                (major_party_races['district'] == row['district']) &
                (major_party_races['district_level'] == row['district_level']) &
                (major_party_races['party'] != row['party']) &
                (major_party_races['party'].isin(['D', 'R']))
            ]
            has_major_opponent = len(same_race) > 0

            # Calculate vote margin (only if has opponent)
            if has_major_opponent and len(same_race) > 0:
                opponent_pct = same_race.iloc[0]['percentage']
                vote_margin = row['percentage'] - opponent_pct
            else:
                # Unopposed or only third-party opposition - skip for now
                continue

            features_list.append({
                'year': row['year'],
                'district': row['district'],
                'district_level': row['district_level'],
                'candidate': row['candidate'],
                'party': row['party'],
                'percentage': row['percentage'],
                'partisan_lean': partisan_lean,
                'is_incumbent': int(row['is_incumbent']),
                'statewide_environment': environment,
                'has_major_opponent': int(has_major_opponent),
                'is_democrat': int(row['party'] == 'D'),
                'vote_margin': vote_margin
            })

        self.training_data = pd.DataFrame(features_list)

        print(f"  Prepared {len(self.training_data):,} training examples")
        print(f"  Features: partisan_lean, is_incumbent, statewide_environment, is_democrat")
        print(f"  Target: vote_margin")

        return self.training_data

    def train_model(self):
        """
        Train regression model to predict expected vote margin

        The model learns what margin a "replacement level" candidate
        should get based on district/environment factors.
        """
        if self.training_data is None:
            self.prepare_training_data()

        print("\nTraining regression model...")

        # Prepare features (X) and target (y)
        feature_cols = ['partisan_lean', 'is_incumbent', 'statewide_environment', 'is_democrat']
        X = self.training_data[feature_cols]
        y = self.training_data['vote_margin']

        # Train model on all data (we want to predict for same races)
        self.model = LinearRegression()
        self.model.fit(X, y)

        # Calculate R-squared
        r2 = self.model.score(X, y)
        print(f"  Model R² = {r2:.3f}")

        # Show feature importance (coefficients)
        print(f"\n  Feature Coefficients:")
        for feature, coef in zip(feature_cols, self.model.coef_):
            print(f"    {feature:25s}: {coef:+.3f}")
        print(f"    {'intercept':25s}: {self.model.intercept_:+.3f}")

        self.feature_importance = dict(zip(feature_cols, self.model.coef_))

        return self.model

    def calculate_war_scores(self):
        """
        Calculate Political WAR for all candidates

        WAR = Actual Margin - Expected Margin

        Positive WAR = Better than expected (strong candidate)
        Negative WAR = Worse than expected (weak candidate)
        """
        if self.model is None:
            self.train_model()

        print("\nCalculating Political WAR scores...")

        # Predict expected margins
        feature_cols = ['partisan_lean', 'is_incumbent', 'statewide_environment', 'is_democrat']
        X = self.training_data[feature_cols]

        self.training_data['expected_margin'] = self.model.predict(X)
        self.training_data['political_war'] = (
            self.training_data['vote_margin'] - self.training_data['expected_margin']
        )

        print(f"  Calculated WAR for {len(self.training_data):,} candidates")

        return self.training_data

    def get_top_performers(self, party=None, year=None, min_war=None, top_n=20):
        """
        Get top performers by Political WAR score

        Args:
            party: Filter by party ('D' or 'R')
            year: Filter by year
            min_war: Minimum WAR score
            top_n: Number of results to return

        Returns:
            DataFrame of top performers sorted by WAR
        """
        if self.training_data is None or 'political_war' not in self.training_data.columns:
            self.calculate_war_scores()

        df = self.training_data.copy()

        # Apply filters
        if party:
            df = df[df['party'] == party]
        if year:
            df = df[df['year'] == year]
        if min_war:
            df = df[df['political_war'] >= min_war]

        # Sort by WAR
        df = df.sort_values('political_war', ascending=False)

        if top_n:
            df = df.head(top_n)

        return df[[
            'year', 'district', 'district_level', 'candidate', 'party',
            'percentage', 'vote_margin', 'expected_margin', 'political_war',
            'partisan_lean', 'is_incumbent'
        ]]


def main():
    """Demonstrate Political WAR model"""
    print("="*70)
    print("Political WAR (Wins Above Replacement) Model")
    print("="*70)

    # Initialize and train model
    war_model = PoliticalWARModel()
    war_model.prepare_training_data()
    war_model.train_model()
    war_model.calculate_war_scores()

    # Show top Democrats by WAR
    print("\n" + "="*70)
    print("Top 20 Democrats by Political WAR (2018-2024)")
    print("="*70)
    top_dems = war_model.get_top_performers(party='D', top_n=20)
    print(top_dems.to_string(index=False))

    # Show top Republicans by WAR
    print("\n" + "="*70)
    print("Top 20 Republicans by Political WAR (2018-2024)")
    print("="*70)
    top_reps = war_model.get_top_performers(party='R', top_n=20)
    print(top_reps.to_string(index=False))

    # Show 2024 top performers
    print("\n" + "="*70)
    print("Top 2024 Performers by Political WAR")
    print("="*70)
    top_2024 = war_model.get_top_performers(year=2024, top_n=20)
    print(top_2024.to_string(index=False))


if __name__ == "__main__":
    main()
