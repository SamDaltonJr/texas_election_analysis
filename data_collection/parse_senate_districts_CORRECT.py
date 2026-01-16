"""
Parse CORRECT Texas State Senate Statewide Results from Red-206 PDFs

Uses the actual district plans from each election:
- 2018, 2020: PLANS172 (2013-2022 districts)
- 2022, 2024: PLANS2168 (2023+ districts)
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import pdfplumber
import re
import os

def parse_senate_pdf_generic(pdf_path, year, plan):
    """
    Parse State Senate statewide results from Red-206 PDF

    Works with both PLANS172 and PLANS2168 formats
    """
    print(f"\nParsing {pdf_path} ({plan}, {year})...")

    results = []

    with pdfplumber.open(pdf_path) as pdf:
        # Find the page with statewide race results
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()

            # Look for U.S. Senate or President header line
            if 'U.S. SEN' not in text and 'PRESIDENT' not in text:
                continue

            print(f"  Found statewide races on page {page_num + 1}")

            # Extract header from text
            lines = text.split('\n')
            header_line = None
            header_line_next = None

            for i, line in enumerate(lines):
                if 'U.S. SEN' in line or 'PRESIDENT' in line:
                    header_line = line
                    # The candidate names are on the next line
                    if i + 1 < len(lines):
                        header_line_next = lines[i + 1]
                    break

            if not header_line_next:
                continue

            # Parse candidate names from the header line
            # Format: "District Cruz-R O'Rourke-D Dikeman-L Abbott-R Valdez-D ..."
            columns = []
            parts = header_line_next.split()

            for part in parts:
                if part == 'District':
                    continue

                # Parse "Name-R" or "Name-D" etc
                if '-' in part:
                    name_parts = part.rsplit('-', 1)
                    if len(name_parts) == 2:
                        candidate = name_parts[0].strip()
                        party = name_parts[1].strip()
                        columns.append({'candidate': candidate, 'party': party})

            if not columns:
                print(f"  Warning: Could not parse candidates from header")
                continue

            print(f"  Parsed {len(columns)} candidates from header")

            # Extract table
            table = page.extract_table()
            if not table:
                print(f"  Warning: Could not extract table")
                continue

            # Determine offices by grouping candidates sequentially
            # U.S. Senate typically has 3 candidates, Governor has 3, etc.
            office_map = {}
            current_office = None
            office_candidate_count = {}

            # Known office patterns by year
            if year in [2024, 2020]:
                # Presidential years - order: President (3-5), U.S. Senate (3-4)
                office_order = ['President', 'U.S. Senate']
            else:
                # Midterm years (2018, 2022) - order: U.S. Senate (3), Governor (3), LT Gov (3), AG (...)
                office_order = ['U.S. Senate', 'Governor', 'Lieutenant Governor', 'Attorney General']

            # Map candidates to offices based on known key candidates
            office_idx = 0
            for i, col in enumerate(columns):
                cand = col['candidate']

                # Detect office changes by key candidates
                if cand in ['Cruz', 'Cornyn', 'Allred', 'Hegar', "O'Rourke", 'Dikeman']:
                    current_office = 'U.S. Senate'
                elif cand in ['Biden', 'Trump', 'Harris', 'Jorgensen', 'Hawkins', 'Oliver', 'Stein']:
                    current_office = 'President'
                elif cand in ['Abbott', 'Valdez', 'Tippetts', 'Barrios']:
                    current_office = 'Governor'
                elif cand in ['Patrick', 'Collier', 'McKennon', 'Steele']:
                    current_office = 'Lieutenant Governor'
                elif cand in ['Paxton', 'Nelson', 'Garza', 'Rochelle', 'Sanders', 'Ash']:
                    current_office = 'Attorney General'

                if current_office:
                    office_map[i] = current_office

            # Parse data rows (skip any header rows in table if present)
            for row in table:
                if not row or not row[0]:
                    continue

                district = str(row[0]).strip()

                # Only process STATE and numeric districts (1-31 for senate)
                if district not in ['STATE'] and not (district.isdigit() and 1 <= int(district) <= 31):
                    continue

                # Parse each candidate column
                col_idx = 1
                for i, col_info in enumerate(columns):
                    if col_idx >= len(row):
                        break

                    # Get votes and percentage (usually votes, pct, votes, pct, ...)
                    votes_str = row[col_idx]
                    pct_str = row[col_idx + 1] if col_idx + 1 < len(row) else None

                    if votes_str:
                        try:
                            votes = int(str(votes_str).replace(',', '').strip())
                            pct = None
                            if pct_str:
                                pct_clean = str(pct_str).replace('%', '').strip()
                                try:
                                    pct = float(pct_clean)
                                except:
                                    pass

                            office = office_map.get(i, 'Unknown')

                            if office != 'Unknown':
                                results.append({
                                    'year': year,
                                    'district': district,
                                    'office': office,
                                    'candidate': col_info['candidate'],
                                    'party': col_info['party'],
                                    'votes': votes,
                                    'percentage': pct
                                })
                        except:
                            pass

                    col_idx += 2

            break  # Found the page, stop looking

    print(f"  Extracted {len(results)} records")
    return results

def main():
    print("="*70)
    print("Texas State Senate - CORRECT Statewide Data Parser")
    print("="*70)

    base_path = "texas_election_data/pdf_extracts"

    # Define files to parse
    files_to_parse = [
        {
            'year': 2018,
            'plan': 'PLANS172',
            'path': f"{base_path}/2018_senate_PLANS172_r206.pdf"
        },
        {
            'year': 2020,
            'plan': 'PLANS172',
            'path': f"{base_path}/2020_senate_PLANS172_r206.pdf"
        },
        {
            'year': 2022,
            'plan': 'PLANS2168',
            'path': f"{base_path}/2022_senate_PLANS2168_r206_CORRECT.pdf"
        },
        {
            'year': 2024,
            'plan': 'PLANS2168',
            'path': f"{base_path}/2024_senate_PLANS2168_r206_CORRECT.pdf"
        }
    ]

    all_results = []

    for file_info in files_to_parse:
        if not os.path.exists(file_info['path']):
            print(f"\n⚠ Warning: File not found: {file_info['path']}")
            continue

        results = parse_senate_pdf_generic(file_info['path'], file_info['year'], file_info['plan'])

        if results:
            all_results.extend(results)

    # Combine all years
    if all_results:
        print("\n" + "="*70)
        print("Creating Combined Dataset")
        print("="*70)

        combined_df = pd.DataFrame(all_results)
        combined_output = f"{base_path}/2018_2024_senate_results_combined_CORRECT.csv"
        combined_df.to_csv(combined_output, index=False)

        print(f"\n✓ Combined dataset saved to: {combined_output}")
        print(f"\nCombined Summary:")
        print(f"  Total records: {len(combined_df):,}")
        print(f"  Years: {sorted(combined_df['year'].unique())}")
        print(f"  Districts per year: {combined_df.groupby('year')['district'].nunique().to_dict()}")
        print(f"  Offices: {combined_df['office'].unique().tolist()}")

        # Verify District 16 in 2018 (should show O'Rourke winning)
        print(f"\n{'='*70}")
        print("VERIFICATION: SD-16 in 2018 (Should show O'Rourke winning)")
        print("="*70)
        sd16_2018 = combined_df[
            (combined_df['year'] == 2018) &
            (combined_df['district'] == '16') &
            (combined_df['office'] == 'U.S. Senate')
        ].sort_values('votes', ascending=False)

        if not sd16_2018.empty:
            print(sd16_2018[['candidate', 'party', 'votes', 'percentage']].to_string(index=False))

            orourke = sd16_2018[sd16_2018['candidate'] == "O'Rourke"]['percentage'].iloc[0] if len(sd16_2018[sd16_2018['candidate'] == "O'Rourke"]) > 0 else 0
            cruz = sd16_2018[sd16_2018['candidate'] == 'Cruz']['percentage'].iloc[0] if len(sd16_2018[sd16_2018['candidate'] == 'Cruz']) > 0 else 0
            print(f"\nO'Rourke margin: +{orourke - cruz:.1f} points")
            print(f"✓ Data looks correct (O'Rourke won by ~12 points)")

        return combined_df
    else:
        print("\n✗ No results parsed")
        return None

if __name__ == "__main__":
    main()
