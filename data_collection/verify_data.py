import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

# Load combined dataset
df = pd.read_csv('texas_election_data/pdf_extracts/2020_2024_house_district_results_combined.csv')

print('=' * 70)
print('Combined Dataset Summary')
print('=' * 70)
print(f'Total records: {len(df):,}')
print(f'\nRecords by year:')
print(df.groupby('year').size())

print(f'\n\nOffices by year:')
for year in sorted(df['year'].unique()):
    offices = df[df['year']==year]['office'].unique().tolist()
    print(f'\n{year}: {offices}')

print(f'\n\n=== Statewide Results Sample ===\n')
state_results = df[df['district']=='STATE'].sort_values(['year', 'office', 'votes'], ascending=[True, True, False])
print(state_results.to_string(index=False))

print(f'\n\n=== Data Quality Checks ===\n')

# Check for missing districts
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    districts = year_df['district'].unique()
    expected = set(['STATE'] + [str(i) for i in range(1, 151)])
    actual = set(districts)
    missing = expected - actual
    if missing:
        print(f'{year}: Missing {len(missing)} districts: {sorted(list(missing)[:10])}...')
    else:
        print(f'{year}: All 151 entities present (STATE + 150 districts) ✓')

print(f'\n=== Sample District 47 (Swing District) ===\n')
d47 = df[df['district']=='47'].sort_values(['year', 'office'])
print(d47.to_string(index=False))
