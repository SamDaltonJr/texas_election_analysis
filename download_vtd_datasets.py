"""
Download Comprehensive VTD Election Datasets from Texas Capitol Data Portal

These datasets contain VTD-level results for all elections including State House and State Senate races.
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import requests
import os

# Create output directory
output_dir = "texas_election_data/vtd_data"
os.makedirs(output_dir, exist_ok=True)

# Dataset URLs from Capitol Data Portal
datasets = [
    {
        'name': '2024 General VTDs Election Data (2012-2024)',
        'url': 'https://data.capitol.texas.gov/dataset/35b16aee-0bb0-4866-b1ec-859f1f044241/resource/e1cd6332-6a7a-4c78-ad2a-852268f6c7a2/download/2024-general-vtds-election-data.zip',
        'output': f'{output_dir}/2024-general-vtds-election-data.zip'
    },
    {
        'name': '2022 General VTDs Election Data (2012-2022)',
        'url': 'https://data.capitol.texas.gov/dataset/35b16aee-0bb0-4866-b1ec-859f1f044241/resource/b9ebdbdb-3e31-4c98-b158-0e2993b05efc/download/2022-general-vtds-election-data.zip',
        'output': f'{output_dir}/2022-general-vtds-election-data.zip'
    },
    {
        'name': '2020 General VTD Election Data (2012-2020)',
        'url': 'https://data.capitol.texas.gov/dataset/35b16aee-0bb0-4866-b1ec-859f1f044241/resource/5af9f5e2-ca14-4e5d-880e-3c3cd891d3ed/download/2020-general-vtd-election-data-2020.zip',
        'output': f'{output_dir}/2020-general-vtd-election-data-2020.zip'
    }
]

print("="*80)
print("Downloading Comprehensive VTD Election Datasets")
print("="*80)

for dataset in datasets:
    print(f"\nDownloading: {dataset['name']}")
    print(f"URL: {dataset['url']}")

    try:
        response = requests.get(dataset['url'], stream=True, timeout=300)

        if response.status_code == 200:
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            size_mb = total_size / (1024 * 1024)

            print(f"Size: {size_mb:.1f} MB")
            print("Downloading...", end='', flush=True)

            # Download with progress
            downloaded = 0
            chunk_size = 8192

            with open(dataset['output'], 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                        print(f"\rDownloading... {progress:.1f}%", end='', flush=True)

            print(f"\rDownloaded successfully: {dataset['output']}")
        else:
            print(f"Failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"Error: {str(e)}")

print("\n" + "="*80)
print("Download Complete")
print("="*80)
print(f"Files saved to: {output_dir}/")
