"""
Parse Texas Ethics Commission Campaign Finance Data

Extracts total expenditures for State House, State Senate, and statewide
candidates for elections 2018-2024.

Data source: https://www.ethics.state.tx.us/search/cf/
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import os


def parse_tec_cover_data():
    """
    Parse TEC cover sheet data to get campaign finance totals

    The cover.csv file contains report summaries with total contributions
    and expenditures for each filing period.
    """
    print("="*70)
    print("Parsing Texas Ethics Commission Campaign Finance Data")
    print("="*70)

    cover_file = 'texas_election_data/campaign_finance/cover.csv'

    if not os.path.exists(cover_file):
        print(f"\n✗ Error: {cover_file} not found")
        print("  Please extract cover.csv from TEC_CF_CSV.zip first")
        return None

    print(f"\nLoading {cover_file}...")

    # Read cover sheet data
    # Key columns:
    # - filerIdent: Unique filer ID
    # - filerName: Candidate/committee name
    # - filerSeekOfficeCd: Office code (STATEREP, STATESENATE, GOVERNOR, etc.)
    # - filerSeekOfficeDistrict: District number
    # - reportTypeCd1: Report type (30DAY, 8DAY, SEMIANN, etc.)
    # - periodStartDt, periodEndDt: Reporting period
    # - totalContribAmount: Total contributions for period
    # - totalExpendAmount: Total expenditures for period
    # - electionDt: Election date
    # - electionTypeCd: PRIMARY, GENERAL, RUNOFF, etc.

    # Due to large file size, read in chunks
    chunk_size = 50000
    chunks = []

    for chunk in pd.read_csv(cover_file, chunksize=chunk_size, low_memory=False):
        # Filter to relevant offices
        relevant_offices = [
            'STATEREP',  # State House
            'STATESEN',  # State Senate
            'GOVERNOR',
            'LTGOVERNOR',
            'ATTYGEN',  # Attorney General
            'COMPTROLLER',
            'COMPTROLLR'  # Alternative spelling
        ]

        chunk_filtered = chunk[
            chunk['filerSeekOfficeCd'].isin(relevant_offices)
        ].copy()

        if len(chunk_filtered) > 0:
            chunks.append(chunk_filtered)

    if not chunks:
        print("\n✗ No relevant filings found")
        return None

    df = pd.concat(chunks, ignore_index=True)

    print(f"  Loaded {len(df):,} relevant campaign finance reports")
    print(f"  Offices: {df['filerSeekOfficeCd'].unique().tolist()}")

    return df


def aggregate_spending_by_candidate(df):
    """
    Aggregate total spending by candidate for each election cycle

    Groups reports by candidate and election year, summing expenditures
    """
    print("\nAggregating spending by candidate and election...")

    # Convert dates
    df['periodEndDt'] = pd.to_datetime(df['periodEndDt'], format='%Y%m%d', errors='coerce')
    df['electionDt'] = pd.to_datetime(df['electionDt'], format='%Y%m%d', errors='coerce')

    # Extract election year from election date or period end date
    df['election_year'] = df['electionDt'].dt.year
    df['election_year'] = df['election_year'].fillna(df['periodEndDt'].dt.year)

    # Filter to our election years
    df = df[df['election_year'].isin([2018, 2020, 2022, 2024])].copy()

    # Filter to general election reports (exclude primaries for now)
    # Report types: PRIMARY, GENERAL, RUNOFF, SPECIAL, etc.
    general_election_types = ['GENERAL', 'RUNOFF', '8DAY', '30DAY', 'SEMIANN', 'ANNUAL']

    # Convert totalExpendAmount to numeric
    df['totalExpendAmount'] = pd.to_numeric(df['totalExpendAmount'], errors='coerce').fillna(0)

    # Group by candidate and election year
    aggregated = df.groupby([
        'filerIdent',
        'filerName',
        'filerSeekOfficeCd',
        'filerSeekOfficeDistrict',
        'election_year'
    ], dropna=False).agg({
        'totalExpendAmount': 'sum',
        'reportInfoIdent': 'count'  # Number of reports filed
    }).reset_index()

    aggregated.columns = [
        'filer_id',
        'candidate_name',
        'office',
        'district',
        'year',
        'total_expenditures',
        'num_reports'
    ]

    # Clean district field (remove leading zeros, handle NaN)
    aggregated['district'] = aggregated['district'].fillna('')
    aggregated['district'] = aggregated['district'].astype(str).str.strip().str.lstrip('0')
    aggregated.loc[aggregated['district'] == '', 'district'] = None

    # Sort by expenditures
    aggregated = aggregated.sort_values(['year', 'office', 'total_expenditures'], ascending=[False, True, False])

    print(f"\n  Aggregated to {len(aggregated):,} candidate-year records")
    print(f"\n  Summary by year and office:")
    summary = aggregated.groupby(['year', 'office']).agg({
        'total_expenditures': ['count', 'sum', 'mean', 'median']
    }).round(0)
    print(summary.to_string())

    return aggregated


def save_finance_data(df):
    """Save aggregated finance data to CSV"""
    output_file = 'texas_election_data/campaign_finance/candidate_spending_2018_2024.csv'
    df.to_csv(output_file, index=False)

    print(f"\n✓ Saved to: {output_file}")

    # Show top spenders by category
    print("\n" + "="*70)
    print("Top 10 Spenders by Office (2018-2024)")
    print("="*70)

    for office in ['STATEREP', 'STATESEN', 'GOVERNOR']:
        office_df = df[df['office'] == office].nlargest(10, 'total_expenditures')
        if len(office_df) > 0:
            print(f"\n{office}:")
            print(office_df[['year', 'district', 'candidate_name', 'total_expenditures']].to_string(index=False))

    return output_file


def main():
    # Parse TEC data
    df = parse_tec_cover_data()

    if df is None:
        return

    # Aggregate by candidate
    aggregated = aggregate_spending_by_candidate(df)

    # Save results
    output_file = save_finance_data(aggregated)

    print(f"\n{'='*70}")
    print("Next Steps")
    print("="*70)
    print("1. Match this spending data to election results")
    print("2. Add spending as a variable to Political WAR model")
    print("3. Analyze impact of spending on vote margin")

    return aggregated


if __name__ == "__main__":
    main()
