"""
Parse U.S. Congressional Race Results from VTD Data

Extracts actual U.S. House races (not statewide races broken down by congressional district)
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import re
from pathlib import Path

def extract_congressional_races_from_vtd(csv_path, year):
    """
    Extract U.S. House races from VTD data

    Parameters:
    - csv_path: Path to the General_Election_Returns.csv file
    - year: Election year

    Returns:
    - DataFrame with district-level aggregated results
    """
    print(f"Processing {year} General Election...")

    # Read VTD data
    df = pd.read_csv(csv_path)

    # Filter to U.S. Rep races
    # Office format: "U.S. Rep 30", "U.S. Rep 1", etc.
    congress_races = df[
        df['Office'].str.contains('U.S. Rep', na=False, regex=False)
    ].copy()

    print(f"  Found {len(congress_races)} VTD-level records for U.S. House races")

    # Extract district number from office name
    # "U.S. Rep 30" -> district="30"
    def parse_office(office_str):
        if pd.isna(office_str):
            return None

        if 'U.S. Rep' in office_str:
            match = re.search(r'U.S. Rep (\d+)', office_str)
            if match:
                return match.group(1)

        return None

    congress_races['district'] = congress_races['Office'].apply(parse_office)

    # Drop rows where we couldn't parse the district
    congress_races = congress_races.dropna(subset=['district'])

    print(f"  Parsed {len(congress_races['district'].unique())} unique congressional districts")

    # Aggregate VTD-level data to district level
    # Group by district, candidate, party and sum votes
    district_results = congress_races.groupby(
        ['district', 'Name', 'Party']
    ).agg({
        'Votes': 'sum'
    }).reset_index()

    # Rename columns to match our standard format
    district_results = district_results.rename(columns={
        'Name': 'candidate',
        'Party': 'party',
        'Votes': 'votes'
    })

    # Calculate percentages within each district race
    # Get total votes per district
    district_totals = district_results.groupby('district')['votes'].sum().reset_index()
    district_totals = district_totals.rename(columns={'votes': 'total_votes'})

    # Merge and calculate percentage
    district_results = district_results.merge(
        district_totals,
        on='district',
        how='left'
    )

    district_results['percentage'] = (
        district_results['votes'] / district_results['total_votes'] * 100
    ).round(1)

    # Add year and office
    district_results['year'] = year
    district_results['office'] = 'U.S. Representative'

    # Reorder columns
    district_results = district_results[[
        'year', 'district', 'office', 'candidate', 'party', 'votes', 'percentage'
    ]]

    # Sort
    district_results = district_results.sort_values(['district', 'votes'],
                                                     ascending=[True, False])

    print(f"  Aggregated to {len(district_results)} candidate records")

    return district_results

def main():
    print("="*80)
    print("PARSING VTD DATA FOR U.S. CONGRESSIONAL RACES (2018, 2020, 2022, 2024)")
    print("="*80)

    vtd_dir = Path("texas_election_data/vtd_data")
    output_dir = Path("texas_election_data/pdf_extracts")

    # Process each year
    years_to_process = [
        (2018, vtd_dir / "2020_data" / "2018_General_Election_Returns.csv"),
        (2020, vtd_dir / "2020_data" / "2020_General_Election_Returns.csv"),
        (2022, vtd_dir / "2022_data" / "2022_General_Election_Returns.csv"),
        (2024, vtd_dir / "2024_data" / "2024_General_Election_Returns.csv")
    ]

    all_congress_races = []

    for year, csv_path in years_to_process:
        print(f"\n{'='*80}")
        print(f"YEAR: {year}")
        print(f"{'='*80}")

        if not csv_path.exists():
            print(f"  ✗ File not found: {csv_path}")
            continue

        # Extract congressional races
        congress_results = extract_congressional_races_from_vtd(csv_path, year)

        print(f"  U.S. House: {len(congress_results)} records across {len(congress_results['district'].unique())} districts")

        all_congress_races.append(congress_results)

    # Combine all years
    if all_congress_races:
        combined_congress = pd.concat(all_congress_races, ignore_index=True)
        output_congress = output_dir / "2018_2024_congressional_races.csv"
        combined_congress.to_csv(output_congress, index=False)
        print(f"\n✓ Saved Congressional races: {output_congress}")
        print(f"  Total records: {len(combined_congress)}")
        print(f"  Years: {sorted(combined_congress['year'].unique())}")
        print(f"  Districts: {len(combined_congress['district'].unique())}")

        # Show sample
        print(f"\n=== SAMPLE DATA ===")
        print(combined_congress.head(10).to_string(index=False))

    print("\n" + "="*80)
    print("PARSING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
