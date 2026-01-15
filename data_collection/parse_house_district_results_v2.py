"""
Parse Texas Election Results by State House District from extracted PDF tables
Version 2 - Uses TABLE sections which have cleaner structure
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import re
import os
import ast

def parse_tables_from_raw_extract(raw_text_file):
    """Extract all table data from the raw PDF extraction"""

    print("="*60)
    print("Parsing 2018 Election Results - Table Extraction Method")
    print("="*60)

    with open(raw_text_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into sections
    sections = content.split('============================================================')

    tables = []
    for i in range(len(sections)):
        if '- TABLE' in sections[i]:
            # Next section contains the table data
            if i + 1 < len(sections):
                table_data = sections[i + 1].strip()
                page_info = sections[i].strip()

                # Extract page number
                page_match = re.search(r'Page (\d+)', page_info)
                page_num = int(page_match.group(1)) if page_match else None

                # Parse each line as a Python list
                rows = []
                for line in table_data.split('\n'):
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        try:
                            row = ast.literal_eval(line)
                            rows.append(row)
                        except:
                            pass

                if rows:
                    tables.append({
                        'page': page_num,
                        'rows': rows
                    })

    print(f"  Extracted {len(tables)} tables from PDF")

    return tables

def identify_race_tables(tables):
    """Identify which tables contain election race results"""

    race_tables = []

    for table in tables:
        # Check if first row contains 'STATE' and vote numbers
        # Race result tables have many numbers and percentages
        if table['rows']:
            first_row = table['rows'][0]

            # Check if this looks like a race results table
            # Should have 'STATE' or district number, followed by many vote counts
            if first_row and len(first_row) > 10:  # Race tables have many columns
                # Check if it has the pattern of votes (numbers with commas) and percentages
                has_numbers = any(',' in str(cell) and str(cell).replace(',', '').replace('.', '').isdigit()
                                  for cell in first_row[1:])

                has_percentages = any('%' in str(cell) for cell in first_row[1:])

                if (first_row[0] == 'STATE' or (isinstance(first_row[0], str) and first_row[0].isdigit())) \
                   and has_numbers and has_percentages:
                    race_tables.append(table)

    print(f"  Identified {len(race_tables)} tables with race results")

    return race_tables

def parse_race_results(race_tables):
    """Parse race results from identified tables"""

    all_results = []

    # Based on the PDF structure, each table has:
    # Column 0: District (STATE, 1, 2, ..., 150)
    # Then groups of 3 columns per race: votes, percentage, votes, percentage, votes, percentage
    # Races: U.S. Senate (3 candidates), Governor (3), Lt. Gov (3), Attorney General (3+)

    race_definitions = [
        {'office': 'U.S. Senate', 'candidates': ['Cruz', "O'Rourke", 'Dikeman'], 'parties': ['REP', 'DEM', 'LIB'], 'col_start': 1},
        {'office': 'Governor', 'candidates': ['Abbott', 'Valdez', 'Tippetts'], 'parties': ['REP', 'DEM', 'LIB'], 'col_start': 7},
        {'office': 'Lieutenant Governor', 'candidates': ['Patrick', 'Collier', 'McKennon'], 'parties': ['REP', 'DEM', 'LIB'], 'col_start': 13},
        {'office': 'Attorney General', 'candidates': ['Paxton', 'Nelson', 'Sanders'], 'parties': ['REP', 'DEM', 'LIB'], 'col_start': 19},
    ]

    for table in race_tables:
        for row in table['rows']:
            if not row or len(row) < 20:  # Skip if not enough columns
                continue

            district = row[0]

            # Skip if not a valid district
            if not (district == 'STATE' or (isinstance(district, str) and district.isdigit())):
                continue

            # Parse each race
            for race_def in race_definitions:
                col_idx = race_def['col_start']

                for i, candidate in enumerate(race_def['candidates']):
                    # Each candidate has 2 columns: votes and percentage
                    vote_col = col_idx + (i * 2)
                    pct_col = col_idx + (i * 2) + 1

                    if vote_col >= len(row) or pct_col >= len(row):
                        break

                    votes_str = str(row[vote_col])
                    pct_str = str(row[pct_col])

                    # Parse votes
                    try:
                        votes = int(votes_str.replace(',', ''))
                    except:
                        continue

                    # Parse percentage
                    try:
                        pct = float(pct_str.replace('%', '').strip())
                    except:
                        continue

                    result = {
                        'year': 2018,
                        'district': district,
                        'office': race_def['office'],
                        'candidate': candidate,
                        'party': race_def['parties'][i],
                        'votes': votes,
                        'percentage': pct
                    }

                    all_results.append(result)

    print(f"  Parsed {len(all_results)} individual candidate records")

    return all_results

def main():
    # Input file from the PDF extraction
    raw_file = "texas_election_data/pdf_extracts/raw_extract_2018.txt"

    if not os.path.exists(raw_file):
        print(f"✗ Error: File not found: {raw_file}")
        print("  Run extract_pdf_election_data.py first to extract the PDF")
        return

    # Step 1: Extract all tables
    tables = parse_tables_from_raw_extract(raw_file)

    # Step 2: Identify race result tables
    race_tables = identify_race_tables(tables)

    # Step 3: Parse the race results
    results = parse_race_results(race_tables)

    if results:
        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Save to CSV
        output_file = "texas_election_data/pdf_extracts/2018_house_district_results.csv"
        df.to_csv(output_file, index=False)

        print(f"\n✓ Saved results to: {output_file}")
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total records: {len(df):,}")
        print(f"Districts: {df['district'].nunique()} (STATE + {df['district'].nunique() - 1} districts)")
        print(f"Offices: {df['office'].unique().tolist()}")
        print(f"Candidates: {df['candidate'].nunique()}")

        print(f"\n{'='*60}")
        print("SAMPLE DATA - First 12 records (District 1, all races)")
        print(f"{'='*60}")
        sample = df[df['district'] == '1'].copy()
        print(sample.to_string(index=False))

        print(f"\n{'='*60}")
        print("STATEWIDE TOTALS")
        print(f"{'='*60}")
        state_totals = df[df['district'] == 'STATE'][['office', 'candidate', 'party', 'votes', 'percentage']].copy()
        state_totals = state_totals.sort_values(['office', 'votes'], ascending=[True, False])
        print(state_totals.to_string(index=False))

        # Verify data quality
        print(f"\n{'='*60}")
        print("DATA QUALITY CHECK")
        print(f"{'='*60}")

        # Check if we have all 150 districts + STATE
        districts_with_data = df['district'].unique()
        expected_districts = set(['STATE'] + [str(i) for i in range(1, 151)])
        actual_districts = set(districts_with_data)
        missing = expected_districts - actual_districts

        if missing:
            print(f"⚠ Missing districts: {sorted(missing, key=lambda x: (x == 'STATE', int(x) if x.isdigit() else 0))}")
        else:
            print(f"✓ All 151 entities present (STATE + 150 districts)")

        # Check records per district
        records_per_district = len(df) / len(districts_with_data)
        print(f"  Average records per district: {records_per_district:.1f}")
        print(f"  Expected: 12 (4 races × 3 candidates)")

        return df
    else:
        print("✗ Failed to parse results")
        return None

if __name__ == "__main__":
    main()
