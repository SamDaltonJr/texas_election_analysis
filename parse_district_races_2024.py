"""
Parse 2024 District Race PDFs (Red-226 Reports)

Extracts actual district race results:
- State House races (State Rep for each district)
- State Senate races (State Sen for each district)
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pdfplumber
import pandas as pd
import re
from pathlib import Path

def extract_district_races(pdf_path, district_type):
    """
    Extract district race results from Red-226 PDF

    Parameters:
    - pdf_path: Path to PDF file
    - district_type: 'house' or 'senate'

    Returns:
    - List of dicts with race results
    """
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) == 0:
            return results

        # Extract text from first page (these are 1-page reports)
        text = pdf.pages[0].extract_text()
        lines = text.split('\n')

        # Extract district number from header
        district_num = None
        for line in lines:
            if district_type == 'house' and 'HOUSE DISTRICT' in line:
                match = re.search(r'HOUSE DISTRICT (\d+)', line)
                if match:
                    district_num = match.group(1)
                    break
            elif district_type == 'senate' and 'SENATE DISTRICT' in line:
                match = re.search(r'SENATE DISTRICT (\d+)', line)
                if match:
                    district_num = match.group(1)
                    break

        if not district_num:
            return results

        # Find the district race section
        if district_type == 'house':
            race_marker = f'State Rep {district_num}'
        else:
            race_marker = f'State Sen {district_num}'

        # Parse line by line to find the race
        in_race_section = False
        race_data = []

        for i, line in enumerate(lines):
            if race_marker in line:
                in_race_section = True
                continue

            if in_race_section:
                # Check if we've reached another race section or end
                if any(marker in line for marker in ['Total Voter Registration', 'For technical reasons',
                                                       'State Rep', 'State Sen', 'U.S. Rep', 'SBOE', 'CCA', 'Sup Ct']):
                    # If it's another State Rep/Sen marker and we're looking for a State Sen, continue searching
                    if district_type == 'senate' and 'State Rep' in line:
                        in_race_section = False
                        continue
                    # Otherwise, we're done with this race
                    break

                # Parse candidate line: "Candidate - Party Votes Percent Votes Percent"
                # Example: "Lambert - R 58,413 81.0% 58,413 81.0%"
                parts = line.split()
                if len(parts) >= 4:
                    # Try to identify candidate-party pattern
                    if '-' in parts:
                        dash_idx = parts.index('-')
                        if dash_idx > 0 and dash_idx < len(parts) - 1:
                            candidate_name = ' '.join(parts[:dash_idx])
                            party = parts[dash_idx + 1]

                            # Extract district votes (first number pair)
                            remaining = parts[dash_idx + 2:]
                            if len(remaining) >= 2:
                                try:
                                    votes_str = remaining[0].replace(',', '')
                                    pct_str = remaining[1].replace('%', '')

                                    votes = int(votes_str)
                                    pct = float(pct_str)

                                    race_data.append({
                                        'year': 2024,
                                        'district': district_num,
                                        'office': f'State {"Representative" if district_type == "house" else "Senator"}',
                                        'candidate': candidate_name,
                                        'party': party,
                                        'votes': votes,
                                        'percentage': pct
                                    })
                                except (ValueError, IndexError):
                                    pass

        results.extend(race_data)

    return results

def parse_all_house_districts():
    """Parse all State House district races"""
    print("Parsing State House District Races...")

    all_results = []
    house_dir = Path("texas_election_data/district_races/house_2024")

    success_count = 0
    unopposed_count = 0
    failed_count = 0

    for i in range(1, 151):
        pdf_path = house_dir / f"house_dist_{i:03d}_2024.pdf"

        if not pdf_path.exists():
            print(f"✗ District {i}: File not found")
            failed_count += 1
            continue

        try:
            results = extract_district_races(str(pdf_path), 'house')

            if len(results) > 0:
                all_results.extend(results)
                candidates = ', '.join([f"{r['candidate']} ({r['party']})" for r in results])
                print(f"✓ District {i:3d}: {candidates}")
                success_count += 1
            else:
                print(f"○ District {i:3d}: No contested race (unopposed or vacant)")
                unopposed_count += 1
        except Exception as e:
            print(f"✗ District {i}: Error - {str(e)}")
            failed_count += 1

    print(f"\nSummary: {success_count} contested, {unopposed_count} unopposed/vacant, {failed_count} failed")

    return pd.DataFrame(all_results)

def parse_all_senate_districts():
    """Parse all State Senate district races"""
    print("Parsing State Senate District Races...")

    all_results = []
    senate_dir = Path("texas_election_data/district_races/senate_2024")

    success_count = 0
    unopposed_count = 0
    failed_count = 0

    for i in range(1, 32):
        pdf_path = senate_dir / f"senate_dist_{i:02d}_2024.pdf"

        if not pdf_path.exists():
            print(f"✗ District {i}: File not found")
            failed_count += 1
            continue

        try:
            results = extract_district_races(str(pdf_path), 'senate')

            if len(results) > 0:
                all_results.extend(results)
                candidates = ', '.join([f"{r['candidate']} ({r['party']})" for r in results])
                print(f"✓ District {i:2d}: {candidates}")
                success_count += 1
            else:
                print(f"○ District {i:2d}: No contested race (unopposed or vacant)")
                unopposed_count += 1
        except Exception as e:
            print(f"✗ District {i}: Error - {str(e)}")
            failed_count += 1

    print(f"\nSummary: {success_count} contested, {unopposed_count} unopposed/vacant, {failed_count} failed")

    return pd.DataFrame(all_results)

def main():
    print("="*70)
    print("PARSING 2024 DISTRICT RACES")
    print("="*70)

    # Parse House districts
    print("\n" + "="*70)
    print("STATE HOUSE DISTRICTS (1-150)")
    print("="*70)
    house_df = parse_all_house_districts()

    # Parse Senate districts
    print("\n" + "="*70)
    print("STATE SENATE DISTRICTS (1-31)")
    print("="*70)
    senate_df = parse_all_senate_districts()

    # Save results
    output_dir = Path("texas_election_data/pdf_extracts")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not house_df.empty:
        house_output = output_dir / "2024_house_races.csv"
        house_df.to_csv(house_output, index=False)
        print(f"\n✓ Saved House races: {house_output}")
        print(f"  Records: {len(house_df)}")

    if not senate_df.empty:
        senate_output = output_dir / "2024_senate_races.csv"
        senate_df.to_csv(senate_output, index=False)
        print(f"\n✓ Saved Senate races: {senate_output}")
        print(f"  Records: {len(senate_df)}")

    # Summary
    print("\n" + "="*70)
    print("PARSING COMPLETE")
    print("="*70)
    print(f"Total House candidates: {len(house_df)}")
    print(f"Total Senate candidates: {len(senate_df)}")
    print(f"Total records: {len(house_df) + len(senate_df)}")

if __name__ == "__main__":
    main()
