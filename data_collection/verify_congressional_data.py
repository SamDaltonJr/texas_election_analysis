import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

# Load combined dataset
df = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_congressional_results_combined.csv')

print('=' * 70)
print('Congressional District Dataset Summary')
print('=' * 70)
print(f'Total records: {len(df):,}')
print(f'\nRecords by year:')
print(df.groupby('year').size())

print(f'\n\nOffices by year:')
for year in sorted(df['year'].unique()):
    offices = df[df['year']==year]['office'].unique().tolist()
    print(f'\n{year}: {offices}')

print(f'\n\n=== Statewide Results ===\n')
state_results = df[df['district']=='STATE'].sort_values(['year', 'office', 'votes'], ascending=[True, True, False])
print(state_results.to_string(index=False))

print(f'\n\n=== Data Quality Checks ===\n')

# Check for missing districts
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    districts = year_df['district'].unique()
    expected = set(['STATE'] + [str(i) for i in range(1, 39)])
    actual = set(districts)
    missing = expected - actual
    if missing:
        print(f'{year}: Missing {len(missing)} districts: {sorted(list(missing)[:10])}...')
    else:
        print(f'{year}: All 39 entities present (STATE + 38 congressional districts) ✓')

print(f'\n=== Sample: District 7 (Houston - Competitive) ===\n')
d7 = df[df['district']=='7'].sort_values(['year', 'office', 'votes'], ascending=[True, True, False])
print(d7.to_string(index=False))

print(f'\n=== Sample: District 32 (Dallas - Competitive) ===\n')
d32 = df[df['district']=='32'].sort_values(['year', 'office', 'votes'], ascending=[True, True, False])
print(d32.to_string(index=False))
