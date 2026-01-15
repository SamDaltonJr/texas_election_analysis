"""
Parse Texas Election Results by Congressional District from PDFs
Handles 2018, 2020, 2022, and 2024 elections
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import pdfplumber
import re
import os

def clean_value(value):
    """Clean and normalize cell values"""
    if value is None:
        return None
    value = str(value).strip()
    value = ' '.join(value.split())
    return value

def parse_percentage(pct_str):
    """Extract percentage from string like '46.5 %' or '46.5%'"""
    if not pct_str:
        return None
    pct_str = str(pct_str).strip().replace('%', '').strip()
    try:
        return float(pct_str)
    except:
        return None

def parse_votes(vote_str):
    """Extract vote count from string like '5,257,513'"""
    if not vote_str:
        return None
    vote_str = str(vote_str).strip().replace(',', '')
    try:
        return int(vote_str)
    except:
        return None

def extract_candidate_data(cell_text):
    """
    Parse candidate data from a cell like 'Biden-D' or 'Trump-R'
    Returns (candidate_name, party)
    """
    if not cell_text:
        return None, None

    cell_text = str(cell_text).strip()

    # Pattern: Name-Party (e.g., 'Biden-D', 'Trump-R', 'O'Rourke-D')
    match = re.match(r"(.+?)-([A-Z]+)$", cell_text)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    return cell_text, None

def parse_congressional_pdf(pdf_path, year):
    """Parse congressional district election PDF for any year"""

    print(f"\nParsing {pdf_path}...")

    results = []

    # Define known candidates by year to help with office assignment
    known_candidates_by_year = {
        2018: {
            'U.S. Senate': ['Cruz', "O'Rourke", 'Dikeman'],
            'Governor': ['Abbott', 'Valdez', 'Tippetts'],
            'Lieutenant Governor': ['Patrick', 'Collier', 'McKennon'],
            'Attorney General': ['Paxton', 'Nelson', 'Sanders']
        },
        2020: {
            'President': ['Biden', 'Trump', 'Jorgensen', 'Hawkins', 'Write-In'],
            'U.S. Senate': ['Cornyn', 'Hegar', 'McKennon', 'Collins'],
            'Railroad Commissioner': ['Castaneda', 'Sterett', 'Gruene']
        },
        2022: {
            'Governor': ['Abbott', "O'Rourke", 'Barrios', 'Tippetts', 'Write-In'],
            'Lieutenant Governor': ['Patrick', 'Collier', 'Steele'],
            'Attorney General': ['Paxton', 'Rochelle', 'Sanders', 'Ash', 'Garza']
        },
        2024: {
            'President': ['Harris', 'Trump', 'Oliver', 'Stein', 'Write-In'],
            'U.S. Senate': ['Cruz', 'Allred', 'Brown', 'Andrus', 'Roche']
        }
    }

    known_candidates = known_candidates_by_year.get(year, {})

    with pdfplumber.open(pdf_path) as pdf:
        # First pass: find candidate info from race headers
        candidates = []

        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            lines = text.split('\n')

            # Find the line with race names
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ['PRESIDENT', 'GOVERNOR', 'U.S. SEN', 'LT. GOVERNOR', 'ATTORNEY']):
                    if i + 1 < len(lines):
                        candidate_line = lines[i + 1]

                        if 'District' in candidate_line:
                            # Parse candidate line
                            candidate_parts = candidate_line.split()

                            for part in candidate_parts[1:]:  # Skip 'District'
                                name, party = extract_candidate_data(part)
                                if name and party:
                                    # Check if we already have this candidate
                                    if not any(c['candidate'] == name for c in candidates):
                                        candidates.append({
                                            'candidate': name,
                                            'party': party,
                                            'office': None
                                        })
                    break

        # Assign offices to candidates based on known candidates
        for cand in candidates:
            for office, names in known_candidates.items():
                if cand['candidate'] in names:
                    cand['office'] = office
                    break
            if not cand['office']:
                cand['office'] = 'Unknown'

        # Second pass: extract all tables from pages with race results only
        # Check which pages have race data
        race_pages = set()
        for page_num in range(len(pdf.pages)):
            text = pdf.pages[page_num].extract_text()
            # Pages with race data have candidate names with party codes
            if any(f'{cand["candidate"]}-{cand["party"]}' in text for cand in candidates if cand):
                race_pages.add(page_num)

        for page_num in race_pages:
            page = pdf.pages[page_num]

            # Extract table
            table = page.extract_table()

            if not table:
                continue

            # Parse data rows
            for row in table:
                if not row or not row[0]:
                    continue

                district = clean_value(row[0])

                # Only process STATE and numeric districts (1-38 for congressional)
                if district not in ['STATE'] and not district.isdigit():
                    continue

                # Extract votes and percentages for each candidate
                col_idx = 1
                for cand_info in candidates:
                    if col_idx < len(row):
                        vote_str = row[col_idx]
                        pct_str = row[col_idx + 1] if col_idx + 1 < len(row) else None

                        votes = parse_votes(vote_str)
                        pct = parse_percentage(pct_str)

                        if votes is not None and cand_info['office'] != 'Unknown':
                            results.append({
                                'year': year,
                                'district': district,
                                'office': cand_info['office'],
                                'candidate': cand_info['candidate'],
                                'party': cand_info['party'],
                                'votes': votes,
                                'percentage': pct
                            })

                        col_idx += 2

    print(f"  Extracted {len(results)} records")
    return results

def main():
    print("="*70)
    print("Texas Congressional District Election Data Parser")
    print("="*70)

    base_path = "texas_election_data/pdf_extracts"

    # Define files to parse
    files_to_parse = [
        {
            'year': 2018,
            'path': f"{base_path}/2018_congressional_c2308.pdf",
            'output': f"{base_path}/2018_congressional_results.csv"
        },
        {
            'year': 2020,
            'path': f"{base_path}/2020_congressional_c2308.pdf",
            'output': f"{base_path}/2020_congressional_results.csv"
        },
        {
            'year': 2022,
            'path': f"{base_path}/2022_congressional_c2308.pdf",
            'output': f"{base_path}/2022_congressional_results.csv"
        },
        {
            'year': 2024,
            'path': f"{base_path}/2024_congressional_c2308.pdf",
            'output': f"{base_path}/2024_congressional_results.csv"
        }
    ]

    all_results = []

    for file_info in files_to_parse:
        if not os.path.exists(file_info['path']):
            print(f"\n⚠ Warning: File not found: {file_info['path']}")
            continue

        results = parse_congressional_pdf(file_info['path'], file_info['year'])

        if results:
            # Save individual year
            df = pd.DataFrame(results)
            df.to_csv(file_info['output'], index=False)
            print(f"  ✓ Saved to {file_info['output']}")

            # Add to combined results
            all_results.extend(results)

            # Show summary
            print(f"\n  Summary for {file_info['year']}:")
            print(f"    Total records: {len(results):,}")
            print(f"    Districts: {df['district'].nunique()}")
            print(f"    Offices: {df['office'].unique().tolist()}")
            print(f"    Candidates: {df['candidate'].nunique()}")

    # Combine all years
    if all_results:
        print("\n" + "="*70)
        print("Creating Combined Dataset")
        print("="*70)

        combined_df = pd.DataFrame(all_results)
        combined_output = f"{base_path}/2018_2024_congressional_results_combined.csv"
        combined_df.to_csv(combined_output, index=False)

        print(f"\n✓ Combined dataset saved to: {combined_output}")
        print(f"\nCombined Summary:")
        print(f"  Total records: {len(combined_df):,}")
        print(f"  Years: {sorted(combined_df['year'].unique())}")
        print(f"  Districts per year: {combined_df.groupby('year')['district'].nunique().to_dict()}")
        print(f"  Offices: {combined_df['office'].unique().tolist()}")
        print(f"  Total candidates: {combined_df['candidate'].nunique()}")

        # Show sample
        print(f"\n{'='*70}")
        print("Sample Data - 2024 Presidential Results, District 7 (Houston)")
        print("="*70)
        sample = combined_df[(combined_df['year'] == 2024) &
                            (combined_df['district'] == '7') &
                            (combined_df['office'] == 'President')]
        if not sample.empty:
            print(sample.to_string(index=False))

        # Show statewide
        print(f"\n{'='*70}")
        print("Statewide Results - 2024 Presidential")
        print("="*70)
        state_2024 = combined_df[(combined_df['year'] == 2024) &
                                 (combined_df['district'] == 'STATE') &
                                 (combined_df['office'] == 'President')].sort_values('votes', ascending=False)
        if not state_2024.empty:
            print(state_2024.to_string(index=False))

        return combined_df
    else:
        print("\n✗ No results parsed")
        return None

if __name__ == "__main__":
    main()
