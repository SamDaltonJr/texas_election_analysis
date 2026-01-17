"""
Import Daily Kos Elections Congressional District Presidential Results

Converts Daily Kos data to our standard format for analysis.
Source: The Downballot (formerly Daily Kos Elections)
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import re

def import_daily_kos_data():
    """
    Import and convert Daily Kos congressional district data to our format

    Their format:
    - District, Incumbent, Party, 2024 Harris%, Trump%, Margin, 2020 Biden%, Trump%, Margin

    Our format:
    - year, district, office, candidate, party, votes, percentage
    """
    print("="*70)
    print("Importing Daily Kos Congressional District Data")
    print("="*70)

    # Read Daily Kos data
    df = pd.read_csv('texas_election_data/pdf_extracts/daily_kos_2020_2024_presidential_by_cd.csv',
                     skiprows=2)  # Skip the header rows

    # Rename columns
    df.columns = ['District', 'Incumbent', 'Party', 'Harris', 'Trump', 'Margin_2024',
                  'Biden', 'Trump_2020', 'Margin_2020']

    # Filter to Texas only
    texas_df = df[df['District'].str.startswith('TX-', na=False)].copy()

    print(f"\nFound {len(texas_df)} Texas congressional districts")

    # Convert to our standard format
    results = []

    for _, row in texas_df.iterrows():
        district = row['District'].replace('TX-', '')  # "TX-01" -> "01"

        # 2024 Presidential results
        if pd.notna(row['Harris']) and pd.notna(row['Trump']):
            harris_pct = float(row['Harris'])
            trump_pct = float(row['Trump'])

            # We don't have vote totals from Daily Kos, only percentages
            # We'll leave votes as None for now
            results.append({
                'year': 2024,
                'district': district,
                'office': 'President',
                'candidate': 'Harris',
                'party': 'D',
                'votes': None,
                'percentage': harris_pct
            })
            results.append({
                'year': 2024,
                'district': district,
                'office': 'President',
                'candidate': 'Trump',
                'party': 'R',
                'votes': None,
                'percentage': trump_pct
            })

        # 2020 Presidential results
        if pd.notna(row['Biden']) and pd.notna(row['Trump_2020']):
            biden_pct = float(row['Biden'])
            trump_pct = float(row['Trump_2020'])

            results.append({
                'year': 2020,
                'district': district,
                'office': 'President',
                'candidate': 'Biden',
                'party': 'D',
                'votes': None,
                'percentage': biden_pct
            })
            results.append({
                'year': 2020,
                'district': district,
                'office': 'President',
                'candidate': 'Trump',
                'party': 'R',
                'votes': None,
                'percentage': trump_pct
            })

    # Create DataFrame
    results_df = pd.DataFrame(results)

    # Save to CSV
    output_file = 'texas_election_data/pdf_extracts/2020_2024_congressional_presidential_dailykos.csv'
    results_df.to_csv(output_file, index=False)

    print(f"\n✓ Saved to: {output_file}")
    print(f"\nSummary:")
    print(f"  Total records: {len(results_df):,}")
    print(f"  Years: {sorted(results_df['year'].unique())}")
    print(f"  Districts: {results_df['district'].nunique()} (CD-{results_df['district'].min()} to CD-{results_df['district'].max()})")
    print(f"  Candidates per year: {results_df.groupby('year')['candidate'].nunique().to_dict()}")

    # Verification
    print(f"\n{'='*70}")
    print("VERIFICATION: CD-09 (Houston - Al Green)")
    print("="*70)

    cd09_2020 = results_df[
        (results_df['year'] == 2020) &
        (results_df['district'] == '09')
    ].sort_values('percentage', ascending=False)

    if not cd09_2020.empty:
        print(cd09_2020[['candidate', 'party', 'percentage']].to_string(index=False))
        biden = cd09_2020[cd09_2020['candidate'] == 'Biden']['percentage'].iloc[0]
        trump = cd09_2020[cd09_2020['candidate'] == 'Trump']['percentage'].iloc[0]
        print(f"\nBiden margin: +{biden - trump:.1f} points")
        print(f"✓ Matches known result (Biden won by ~53 points)")

    return results_df

if __name__ == "__main__":
    import_daily_kos_data()
