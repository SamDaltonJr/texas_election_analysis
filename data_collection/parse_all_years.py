"""
Parse Texas Election Results by State House District from PDFs
Handles 2020, 2022, and 2024 elections
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
    # Remove multiple spaces
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
    # Handle cases with apostrophes in names
    match = re.match(r"(.+?)-([A-Z]+)$", cell_text)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    return cell_text, None

def parse_2020_pdf(pdf_path):
    """Parse 2020 election PDF (Presidential, US Senate, RR Commissioner)"""

    print(f"\nParsing {pdf_path}...")

    results = []

    with pdfplumber.open(pdf_path) as pdf:
        # Start from page 6 where race results begin (0-indexed = page 5)
        for page_num in range(5, len(pdf.pages)):
            page = pdf.pages[page_num]

            # Extract text to find race headers and candidate names
            text = page.extract_text()
            lines = text.split('\n')

            # Find the line with race names (e.g., "PRESIDENT U.S. SEN RR COMM 1")
            race_header_line = None
            candidate_line = None

            for i, line in enumerate(lines):
                if 'PRESIDENT' in line or 'GOVERNOR' in line or 'U.S. SEN' in line:
                    race_header_line = line
                    # Next line should have candidates
                    if i + 1 < len(lines):
                        candidate_line = lines[i + 1]
                    break

            if not race_header_line or not candidate_line or 'District' not in candidate_line:
                continue

            # Parse race headers
            # Example: "PRESIDENT U.S. SEN RR COMM 1"
            race_names = []
            if 'PRESIDENT' in race_header_line:
                race_names.append('President')
            if 'U.S. SEN' in race_header_line:
                race_names.append('U.S. Senate')
            if 'RR COMM' in race_header_line:
                race_names.append('Railroad Commissioner')

            # Parse candidate line
            # Example: "District Biden-D Trump-R Jorgensen-L Hawkins-G Write-In-W Cornyn-R Hegar-D McKennon-L Collins-G Castaneda-D"
            candidate_parts = candidate_line.split()

            candidates = []
            for part in candidate_parts[1:]:  # Skip 'District'
                name, party = extract_candidate_data(part)
                if name and party:
                    candidates.append({
                        'candidate': name,
                        'party': party,
                        'office': None  # Will assign below
                    })

            # Assign offices to candidates based on order
            # Typically: Presidential candidates first, then Senate, then other races
            known_candidates = {
                'President': ['Biden', 'Trump', 'Jorgensen', 'Hawkins', 'Write-In'],
                'U.S. Senate': ['Cornyn', 'Hegar', 'McKennon', 'Collins'],
                'Railroad Commissioner': ['Castaneda', 'Sterett', 'Gruene']
            }

            for cand in candidates:
                for office, names in known_candidates.items():
                    if cand['candidate'] in names:
                        cand['office'] = office
                        break
                if not cand['office']:
                    cand['office'] = 'Unknown'

            # Extract table
            table = page.extract_table()

            if not table or len(table) < 2:
                continue

            # Parse data rows (first row is STATE, rest are districts)
            for row in table:
                if not row or not row[0]:
                    continue

                district = clean_value(row[0])

                # Only process STATE and numeric districts
                if district not in ['STATE'] and not district.isdigit():
                    continue

                # Extract votes and percentages for each candidate
                # Data pattern: District, Vote1, Pct1, Vote2, Pct2, ...
                col_idx = 1
                for cand_info in candidates:
                    if col_idx < len(row):
                        vote_str = row[col_idx]
                        pct_str = row[col_idx + 1] if col_idx + 1 < len(row) else None

                        votes = parse_votes(vote_str)
                        pct = parse_percentage(pct_str)

                        if votes is not None and cand_info['office'] != 'Unknown':
                            results.append({
                                'year': 2020,
                                'district': district,
                                'office': cand_info['office'],
                                'candidate': cand_info['candidate'],
                                'party': cand_info['party'],
                                'votes': votes,
                                'percentage': pct
                            })

                        col_idx += 2  # Move to next candidate (skip vote and pct columns)

            # Continue to next page to get more districts

    print(f"  Extracted {len(results)} records")
    return results

def parse_2022_pdf(pdf_path):
    """Parse 2022 election PDF (Governor, Lt Gov, Attorney General, etc.)"""

    print(f"\nParsing {pdf_path}...")

    results = []

    with pdfplumber.open(pdf_path) as pdf:
        # Start from page 6 where race results begin
        for page_num in range(5, len(pdf.pages)):
            page = pdf.pages[page_num]

            # Extract text to find race headers and candidate names
            text = page.extract_text()
            lines = text.split('\n')

            # Find the line with race names
            race_header_line = None
            candidate_line = None

            for i, line in enumerate(lines):
                if 'GOVERNOR' in line or 'LT. GOVERNOR' in line or 'ATTORNEY' in line:
                    race_header_line = line
                    if i + 1 < len(lines):
                        candidate_line = lines[i + 1]
                    break

            if not race_header_line or not candidate_line or 'District' not in candidate_line:
                continue

            # Parse candidate line
            candidate_parts = candidate_line.split()

            candidates = []
            for part in candidate_parts[1:]:  # Skip 'District'
                name, party = extract_candidate_data(part)
                if name and party:
                    candidates.append({
                        'candidate': name,
                        'party': party,
                        'office': None
                    })

            # Assign offices to candidates
            known_candidates = {
                'Governor': ['Abbott', "O'Rourke", 'Barrios', 'Tippetts', 'Write-In'],
                'Lieutenant Governor': ['Patrick', 'Collier', 'Steele'],
                'Attorney General': ['Paxton', 'Rochelle', 'Sanders', 'Ash', 'Garza']
            }

            for cand in candidates:
                for office, names in known_candidates.items():
                    if cand['candidate'] in names:
                        cand['office'] = office
                        break
                if not cand['office']:
                    cand['office'] = 'Unknown'

            # Extract table
            table = page.extract_table()

            if not table or len(table) < 2:
                continue

            # Parse data rows
            for row in table:
                if not row or not row[0]:
                    continue

                district = clean_value(row[0])

                if district not in ['STATE'] and not district.isdigit():
                    continue

                col_idx = 1
                for cand_info in candidates:
                    if col_idx < len(row):
                        vote_str = row[col_idx]
                        pct_str = row[col_idx + 1] if col_idx + 1 < len(row) else None

                        votes = parse_votes(vote_str)
                        pct = parse_percentage(pct_str)

                        if votes is not None and cand_info['office'] != 'Unknown':
                            results.append({
                                'year': 2022,
                                'district': district,
                                'office': cand_info['office'],
                                'candidate': cand_info['candidate'],
                                'party': cand_info['party'],
                                'votes': votes,
                                'percentage': pct
                            })

                        col_idx += 2

            # Continue to next page to get more districts

    print(f"  Extracted {len(results)} records")
    return results

def parse_2024_pdf(pdf_path):
    """Parse 2024 election PDF (Presidential, US Senate)"""

    print(f"\nParsing {pdf_path}...")

    results = []

    with pdfplumber.open(pdf_path) as pdf:
        # Start from page 6 where race results begin
        for page_num in range(5, len(pdf.pages)):
            page = pdf.pages[page_num]

            # Extract text to find race headers and candidate names
            text = page.extract_text()
            lines = text.split('\n')

            # Find the line with race names
            race_header_line = None
            candidate_line = None

            for i, line in enumerate(lines):
                if 'PRESIDENT' in line or 'U.S. SEN' in line:
                    race_header_line = line
                    if i + 1 < len(lines):
                        candidate_line = lines[i + 1]
                    break

            if not race_header_line or not candidate_line or 'District' not in candidate_line:
                continue

            # Parse candidate line
            candidate_parts = candidate_line.split()

            candidates = []
            for part in candidate_parts[1:]:  # Skip 'District'
                name, party = extract_candidate_data(part)
                if name and party:
                    candidates.append({
                        'candidate': name,
                        'party': party,
                        'office': None
                    })

            # Assign offices to candidates
            known_candidates = {
                'President': ['Harris', 'Trump', 'Oliver', 'Stein', 'Write-In'],
                'U.S. Senate': ['Cruz', 'Allred', 'Brown', 'Andrus', 'Roche']
            }

            for cand in candidates:
                for office, names in known_candidates.items():
                    if cand['candidate'] in names:
                        cand['office'] = office
                        break
                if not cand['office']:
                    cand['office'] = 'Unknown'

            # Extract table
            table = page.extract_table()

            if not table or len(table) < 2:
                continue

            # Parse data rows
            for row in table:
                if not row or not row[0]:
                    continue

                district = clean_value(row[0])

                if district not in ['STATE'] and not district.isdigit():
                    continue

                col_idx = 1
                for cand_info in candidates:
                    if col_idx < len(row):
                        vote_str = row[col_idx]
                        pct_str = row[col_idx + 1] if col_idx + 1 < len(row) else None

                        votes = parse_votes(vote_str)
                        pct = parse_percentage(pct_str)

                        if votes is not None and cand_info['office'] != 'Unknown':
                            results.append({
                                'year': 2024,
                                'district': district,
                                'office': cand_info['office'],
                                'candidate': cand_info['candidate'],
                                'party': cand_info['party'],
                                'votes': votes,
                                'percentage': pct
                            })

                        col_idx += 2

            # Continue to next page to get more districts

    print(f"  Extracted {len(results)} records")
    return results

def main():
    print("="*70)
    print("Texas Election Data Parser - 2020, 2022, 2024")
    print("="*70)

    base_path = "texas_election_data/pdf_extracts"

    # Define files to parse
    files_to_parse = [
        {
            'year': 2020,
            'path': f"{base_path}/2020_planh2316.pdf",
            'parser': parse_2020_pdf,
            'output': f"{base_path}/2020_house_district_results.csv"
        },
        {
            'year': 2022,
            'path': f"{base_path}/2022_planh2176_full.pdf",
            'parser': parse_2022_pdf,
            'output': f"{base_path}/2022_house_district_results.csv"
        },
        {
            'year': 2024,
            'path': f"{base_path}/2024_planh2176_full.pdf",
            'parser': parse_2024_pdf,
            'output': f"{base_path}/2024_house_district_results.csv"
        }
    ]

    all_results = []

    for file_info in files_to_parse:
        if not os.path.exists(file_info['path']):
            print(f"\n⚠ Warning: File not found: {file_info['path']}")
            continue

        results = file_info['parser'](file_info['path'])

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
        combined_output = f"{base_path}/2020_2024_house_district_results_combined.csv"
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
        print("Sample Data - 2024 Presidential Results, District 1")
        print("="*70)
        sample = combined_df[(combined_df['year'] == 2024) &
                            (combined_df['district'] == '1') &
                            (combined_df['office'] == 'President')]
        if not sample.empty:
            print(sample.to_string(index=False))

        return combined_df
    else:
        print("\n✗ No results parsed")
        return None

if __name__ == "__main__":
    main()
