import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

# Load combined dataset
df = pd.read_csv('texas_election_data/pdf_extracts/2018_2024_senate_results_combined.csv')

print('=' * 70)
print('State Senate District Dataset Summary')
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
print(state_results[['year', 'office', 'candidate', 'party', 'votes', 'percentage']].to_string(index=False))

print(f'\n\n=== Data Quality Checks ===\n')

# Check for missing districts
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    districts = year_df['district'].unique()
    expected = set(['STATE'] + [str(i) for i in range(1, 32)])
    actual = set(districts)
    missing = expected - actual
    if missing:
        print(f'{year}: Missing {len(missing)} districts: {sorted(list(missing)[:10])}...')
    else:
        print(f'{year}: All 32 entities present (STATE + 31 State Senate districts) ✓')

print(f'\n=== Sample: District 10 (Austin Area) ===\n')
d10 = df[df['district']=='10'].sort_values(['year', 'office', 'votes'], ascending=[True, True, False])
print(d10[['year', 'office', 'candidate', 'party', 'votes', 'percentage']].to_string(index=False))

print(f'\n=== Sample: District 21 (San Antonio/RGV) ===\n')
d21 = df[df['district']=='21'].sort_values(['year', 'office', 'votes'], ascending=[True, True, False])
print(d21[['year', 'office', 'candidate', 'party', 'votes', 'percentage']].to_string(index=False))
