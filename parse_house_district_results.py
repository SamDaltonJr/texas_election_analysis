"""
Parse Texas Election Results by State House District from Capitol Data Portal PDFs
Converts election results into clean CSV format for analysis
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import re
import os

def parse_2018_results(raw_text_file):
    """Parse the 2018 election results from extracted PDF text"""

    print("="*60)
    print("Parsing 2018 Election Results by State House District")
    print("="*60)

    with open(raw_text_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the section with race results
    # Look for the line with candidate names
    pattern = r"District Cruz-R O'Rourke-D.*?Paxton-R"

    matches = re.findall(pattern, content)

    if not matches:
        print("✗ Could not find race results in file")
        return None

    print(f"Found {len(matches)} result sections")

    # Extract all result lines
    # Pattern: starts with STATE or a number, followed by vote counts
    all_results = []

    # Split content into lines
    lines = content.split('\n')

    # Track if we're in a results section
    in_results = False
    current_races = []

    for i, line in enumerate(lines):
        # Check if this is a header line with candidate names
        if 'Cruz-R' in line and "O'Rourke-D" in line:
            in_results = True
            # Extract race names and candidates from header
            # Example: "U.S. SEN GOVERNOR LT. GOVERNOR ATTORNEY GEN"
            header_line = lines[i-1] if i > 0 else ""
            candidate_line = line

            # Parse the races from this section
            print(f"\n  Found results section: {header_line[:60]}...")

            # Identify races (very simplified - adjust based on actual structure)
            races = []
            if 'Cruz-R' in candidate_line:
                races.append({'office': 'U.S. Senate', 'candidates': ['Cruz-R', "O'Rourke-D", 'Dikeman-L']})
            if 'Abbott-R' in candidate_line:
                races.append({'office': 'Governor', 'candidates': ['Abbott-R', 'Valdez-D', 'Tippetts-L']})
            if 'Patrick-R' in candidate_line:
                races.append({'office': 'Lieutenant Governor', 'candidates': ['Patrick-R', 'Collier-D', 'McKennon-L']})
            if 'Paxton-R' in candidate_line:
                races.append({'office': 'Attorney General', 'candidates': ['Paxton-R', 'Nelson-D', 'Sanders-L']})

            current_races = races
            continue

        # If we're in results section, look for data rows
        if in_results:
            # Check if line starts with STATE or a district number (1-150)
            match = re.match(r"^(STATE|\d{1,3})\s+(.+)", line)

            if match:
                district = match.group(1)
                data_str = match.group(2)

                # Parse the numbers and percentages
                # Pattern: number, percentage, number, percentage, etc.
                numbers = re.findall(r'([\d,]+)\s+([\d.]+\s*%)', data_str)

                if numbers and len(numbers) >= 3:  # At least one race with 3 candidates
                    # Group into sets of 3 (one per candidate per race)
                    result = {
                        'district': district,
                        'raw_data': data_str,
                        'vote_groups': numbers
                    }
                    all_results.append(result)

            # Check if we've left the results section
            if 'For technical reasons' in line or 'Page' in line:
                in_results = False

    print(f"\n  Extracted {len(all_results)} district result rows")

    # Convert to structured data
    structured_data = []

    for result in all_results:
        district = result['district']
        vote_groups = result['vote_groups']

        # Assume 3 candidates per race, 4 races total = 12 vote/pct pairs
        # U.S. Senate: positions 0-2
        # Governor: positions 3-5
        # Lt. Governor: positions 6-8
        # Attorney General: positions 9-11

        if len(vote_groups) >= 12:
            races_data = [
                {
                    'race': 'U.S. Senate',
                    'candidates': [
                        ('Cruz', 'REP', vote_groups[0]),
                        ("O'Rourke", 'DEM', vote_groups[1]),
                        ('Dikeman', 'LIB', vote_groups[2])
                    ]
                },
                {
                    'race': 'Governor',
                    'candidates': [
                        ('Abbott', 'REP', vote_groups[3]),
                        ('Valdez', 'DEM', vote_groups[4]),
                        ('Tippetts', 'LIB', vote_groups[5])
                    ]
                },
                {
                    'race': 'Lieutenant Governor',
                    'candidates': [
                        ('Patrick', 'REP', vote_groups[6]),
                        ('Collier', 'DEM', vote_groups[7]),
                        ('McKennon', 'LIB', vote_groups[8])
                    ]
                },
                {
                    'race': 'Attorney General',
                    'candidates': [
                        ('Paxton', 'REP', vote_groups[9]),
                        ('Nelson', 'DEM', vote_groups[10]),
                        ('Sanders', 'LIB', vote_groups[11])
                    ]
                }
            ]

            for race_info in races_data:
                for candidate, party, (votes_str, pct_str) in race_info['candidates']:
                    # Clean up numbers
                    votes = int(votes_str.replace(',', ''))
                    pct = float(pct_str.replace('%', '').strip())

                    structured_data.append({
                        'year': 2018,
                        'district': district,
                        'office': race_info['race'],
                        'candidate': candidate,
                        'party': party,
                        'votes': votes,
                        'percentage': pct
                    })

    print(f"\n  Created {len(structured_data)} individual candidate records")

    # Convert to DataFrame
    df = pd.DataFrame(structured_data)

    return df

def main():
    # Input file from the PDF extraction
    raw_file = "texas_election_data/pdf_extracts/raw_extract_2018.txt"

    if not os.path.exists(raw_file):
        print(f"✗ Error: File not found: {raw_file}")
        print("  Run extract_pdf_election_data.py first to extract the PDF")
        return

    # Parse the results
    df = parse_2018_results(raw_file)

    if df is not None:
        # Save to CSV
        output_file = "texas_election_data/pdf_extracts/2018_house_district_results.csv"
        df.to_csv(output_file, index=False)

        print(f"\n✓ Saved results to: {output_file}")
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total records: {len(df):,}")
        print(f"Districts: {df['district'].nunique()}")
        print(f"Offices: {df['office'].unique().tolist()}")
        print(f"Candidates: {df['candidate'].nunique()}")

        print(f"\n{'='*60}")
        print("SAMPLE DATA")
        print(f"{'='*60}")
        print(df.head(15).to_string())

        print(f"\n{'='*60}")
        print("STATEWIDE TOTALS")
        print(f"{'='*60}")
        state_totals = df[df['district'] == 'STATE'][['office', 'candidate', 'party', 'votes', 'percentage']]
        print(state_totals.to_string())

        return df
    else:
        print("✗ Failed to parse results")
        return None

if __name__ == "__main__":
    main()
