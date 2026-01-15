"""
Download Texas State Senate district election PDFs from Texas Capitol Data Portal
"""

import requests
import os

# Create output directory
output_dir = "texas_election_data/pdf_extracts"
os.makedirs(output_dir, exist_ok=True)

# State Senate PDFs to download
# Pattern: plans####r206_YYg.pdf
# Based on the patterns for House (planh) and Congressional (planc), trying PLANS2168 and PLANS2148

senate_pdfs = [
    # Try different plan numbers - State Senate was redistricted in 2021
    # PLANS2168 is likely the 2021 redistricted plan
    {
        'year': 2018,
        'urls': [
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/89f7b7ed-0d99-4f64-8a29-18f8f6a6e2ce/download/plans2168r206_18g.pdf',
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/b6eac4c8-bb68-4857-8755-2c1cd0f6e37c/download/plans2148r206_18g.pdf',
        ],
        'output': f'{output_dir}/2018_senate_s2168.pdf'
    },
    {
        'year': 2020,
        'urls': [
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/2d6e2fb7-6bb1-4c94-882b-7e56c4c0b891/download/plans2168r206_20g.pdf',
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/85e7dfeb-c27d-44cb-b4a4-3f0a5c5f5e5a/download/plans2148r206_20g.pdf',
        ],
        'output': f'{output_dir}/2020_senate_s2168.pdf'
    },
    {
        'year': 2022,
        'urls': [
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/d0e8f3c8-3cb6-4e63-8f1e-b7c9f6d4e9f0/download/plans2168_r206_election22g.pdf',
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/f8c8c5e3-9c4f-4f63-9f1e-c7b9f6d4e9f1/download/plans2148_r206_election22g.pdf',
        ],
        'output': f'{output_dir}/2022_senate_s2168.pdf'
    },
    {
        'year': 2024,
        'urls': [
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d/download/plans2168_r206_election24g.pdf',
            'https://data.capitol.texas.gov/dataset/c53f8304-ee95-4f18-932f-e3e146dde0d1/resource/b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e/download/plans2148_r206_election24g.pdf',
        ],
        'output': f'{output_dir}/2024_senate_s2168.pdf'
    }
]

print("="*70)
print("Searching for Texas State Senate District PDFs")
print("="*70)

# Let's first search the portal to find the correct URLs
print("\nSearching Texas Capitol Data Portal...")
print("Looking for State Senate election data...\n")

# Instead of guessing URLs, let's search for the datasets
search_url = "https://data.capitol.texas.gov/api/3/action/package_search"
params = {
    'q': 'senate election analysis red-206',
    'rows': 20
}

try:
    response = requests.get(search_url, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['result']['count'] > 0:
            print(f"Found {data['result']['count']} datasets related to State Senate elections:\n")

            for dataset in data['result']['results']:
                title = dataset.get('title', 'N/A')
                name = dataset.get('name', 'N/A')

                if 'senate' in title.lower() or 'plans' in name.lower():
                    print(f"Dataset: {title}")
                    print(f"  Name: {name}")

                    if 'resources' in dataset:
                        for resource in dataset['resources']:
                            resource_name = resource.get('name', '')
                            resource_url = resource.get('url', '')

                            # Look for election PDFs (18g, 20g, 22g, 24g patterns)
                            if any(year in resource_name.lower() for year in ['18g', '20g', '22g', '24g']):
                                print(f"    Resource: {resource_name}")
                                print(f"    URL: {resource_url}")
                    print()
        else:
            print("No datasets found. Will try direct dataset URLs...\n")
    else:
        print(f"Search failed with status {response.status_code}\n")
except Exception as e:
    print(f"Search error: {e}\n")

print("\n" + "="*70)
print("Attempting to download from known dataset patterns...")
print("="*70)

# Try the PLANS2168 dataset (2020 Census redistricting)
base_url = "https://data.capitol.texas.gov/dataset/plans2168/resource"

# Resource IDs to try (these would need to be found from the portal)
potential_files = [
    ('2018', 'plans2168r206_18g.pdf'),
    ('2020', 'plans2168r206_20g.pdf'),
    ('2022', 'plans2168_r206_election22g.pdf'),
    ('2024', 'plans2168_r206_election24g.pdf'),
]

print("\nNote: You may need to manually find these PDFs at:")
print("https://data.capitol.texas.gov/dataset")
print("Search for: 'PLANS2168' or 'State Senate election analysis'\n")

print("Once you find the correct dataset, the PDFs should follow this pattern:")
for year, filename in potential_files:
    print(f"  {year}: {filename}")
