"""
Parse VTD-level election data to extract district race results for 2018-2022

Aggregates Voter Tabulation District (VTD) level data to district-level results
for State House and State Senate races.
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import re
from pathlib import Path

def extract_district_races_from_vtd(csv_path, year):
    """
    Extract State House and State Senate races from VTD data

    Parameters:
    - csv_path: Path to the General_Election_Returns.csv file
    - year: Election year

    Returns:
    - DataFrame with district-level aggregated results
    """
    print(f"Processing {year} General Election...")

    # Read VTD data
    df = pd.read_csv(csv_path)

    # Filter to State House and State Senate races
    state_races = df[
        df['Office'].str.contains('State Rep|State Sen', na=False, regex=True)
    ].copy()

    print(f"  Found {len(state_races)} VTD-level records for district races")

    # Extract district number from office name
    # "State Rep 71" -> office="State Representative", district="71"
    # "State Sen 10" -> office="State Senator", district="10"
    def parse_office(office_str):
        if pd.isna(office_str):
            return None, None

        if 'State Rep' in office_str:
            match = re.search(r'State Rep (\d+)', office_str)
            if match:
                return 'State Representative', match.group(1)
        elif 'State Sen' in office_str:
            match = re.search(r'State Sen (\d+)', office_str)
            if match:
                return 'State Senator', match.group(1)

        return None, None

    state_races[['office_clean', 'district']] = state_races['Office'].apply(
        lambda x: pd.Series(parse_office(x))
    )

    # Drop rows where we couldn't parse the district
    state_races = state_races.dropna(subset=['office_clean', 'district'])

    print(f"  Parsed {len(state_races['district'].unique())} unique districts")

    # Aggregate VTD-level data to district level
    # Group by district, office, candidate, party and sum votes
    district_results = state_races.groupby(
        ['district', 'office_clean', 'Name', 'Party']
    ).agg({
        'Votes': 'sum'
    }).reset_index()

    # Rename columns to match our standard format
    district_results = district_results.rename(columns={
        'office_clean': 'office',
        'Name': 'candidate',
        'Party': 'party',
        'Votes': 'votes'
    })

    # Calculate percentages within each district race
    # Get total votes per district
    district_totals = district_results.groupby(['district', 'office'])['votes'].sum().reset_index()
    district_totals = district_totals.rename(columns={'votes': 'total_votes'})

    # Merge and calculate percentage
    district_results = district_results.merge(
        district_totals,
        on=['district', 'office'],
        how='left'
    )

    district_results['percentage'] = (
        district_results['votes'] / district_results['total_votes'] * 100
    ).round(1)

    # Add year
    district_results['year'] = year

    # Reorder columns
    district_results = district_results[[
        'year', 'district', 'office', 'candidate', 'party', 'votes', 'percentage'
    ]]

    # Sort
    district_results = district_results.sort_values(['district', 'office', 'votes'],
                                                     ascending=[True, True, False])

    print(f"  Aggregated to {len(district_results)} candidate records")

    return district_results

def main():
    print("="*80)
    print("PARSING VTD DATA FOR DISTRICT RACES (2018, 2020, 2022)")
    print("="*80)

    vtd_dir = Path("texas_election_data/vtd_data")
    output_dir = Path("texas_election_data/pdf_extracts")

    # Process each year
    years_to_process = [
        (2018, vtd_dir / "2020_data" / "2018_General_Election_Returns.csv"),
        (2020, vtd_dir / "2020_data" / "2020_General_Election_Returns.csv"),
        (2022, vtd_dir / "2022_data" / "2022_General_Election_Returns.csv")
    ]

    all_house_races = []
    all_senate_races = []

    for year, csv_path in years_to_process:
        print(f"\n{'='*80}")
        print(f"YEAR: {year}")
        print(f"{'='*80}")

        if not csv_path.exists():
            print(f"  ✗ File not found: {csv_path}")
            continue

        # Extract district races
        district_results = extract_district_races_from_vtd(csv_path, year)

        # Split into House and Senate
        house = district_results[district_results['office'] == 'State Representative'].copy()
        senate = district_results[district_results['office'] == 'State Senator'].copy()

        print(f"  State House: {len(house)} records across {len(house['district'].unique())} districts")
        print(f"  State Senate: {len(senate)} records across {len(senate['district'].unique())} districts")

        all_house_races.append(house)
        all_senate_races.append(senate)

    # Combine all years
    if all_house_races:
        combined_house = pd.concat(all_house_races, ignore_index=True)
        output_house = output_dir / "2018_2022_house_races.csv"
        combined_house.to_csv(output_house, index=False)
        print(f"\n✓ Saved House races: {output_house}")
        print(f"  Total records: {len(combined_house)}")
        print(f"  Years: {sorted(combined_house['year'].unique())}")
        print(f"  Districts: {len(combined_house['district'].unique())}")

    if all_senate_races:
        combined_senate = pd.concat(all_senate_races, ignore_index=True)
        output_senate = output_dir / "2018_2022_senate_races.csv"
        combined_senate.to_csv(output_senate, index=False)
        print(f"\n✓ Saved Senate races: {output_senate}")
        print(f"  Total records: {len(combined_senate)}")
        print(f"  Years: {sorted(combined_senate['year'].unique())}")
        print(f"  Districts: {len(combined_senate['district'].unique())}")

    print("\n" + "="*80)
    print("PARSING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
