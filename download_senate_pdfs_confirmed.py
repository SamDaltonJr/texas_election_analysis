"""
Download Texas State Senate district election PDFs - Confirmed URLs from PLANS2168
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import requests
import os

# Create output directory
output_dir = "texas_election_data/pdf_extracts"
os.makedirs(output_dir, exist_ok=True)

# Confirmed URLs from PLANS2168 dataset (r206 = Election Analysis reports)
senate_pdfs = [
    {
        'year': 2018,
        'url': 'https://data.capitol.texas.gov/dataset/70836384-f10c-423d-a36e-748d7e000872/resource/2084b03b-34f3-41b3-8448-18f0a9804846/download/plans2168r206_18g.pdf',
        'output': f'{output_dir}/2018_senate_s2168.pdf'
    },
    {
        'year': 2020,
        'url': 'https://data.capitol.texas.gov/dataset/70836384-f10c-423d-a36e-748d7e000872/resource/88950895-32d4-406b-afe5-7169489d083d/download/plans2168r206_20g.pdf',
        'output': f'{output_dir}/2020_senate_s2168.pdf'
    },
    {
        'year': 2022,
        'url': 'https://data.capitol.texas.gov/dataset/70836384-f10c-423d-a36e-748d7e000872/resource/81e493fc-ae94-406a-bbd1-1de56adc5932/download/plans2168_r206_election22g.pdf',
        'output': f'{output_dir}/2022_senate_s2168.pdf'
    },
    {
        'year': 2024,
        'url': 'https://data.capitol.texas.gov/dataset/70836384-f10c-423d-a36e-748d7e000872/resource/34ca3850-1a27-4696-8bdf-5cb82869792a/download/plans2168_r206_election24g.pdf',
        'output': f'{output_dir}/2024_senate_s2168.pdf'
    }
]

print("="*70)
print("Downloading Texas State Senate District PDFs (PLANS2168)")
print("="*70)

for pdf_info in senate_pdfs:
    year = pdf_info['year']
    url = pdf_info['url']
    output_path = pdf_info['output']

    print(f"\n{year}: Downloading from {url.split('/')[-1]}...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        file_size = len(response.content) / 1024  # KB
        print(f"  ✓ Downloaded: {output_path} ({file_size:.1f} KB)")

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download: {e}")

print("\n" + "="*70)
print("Download Complete!")
print("="*70)
print(f"\nFiles saved to: {output_dir}/")
print("\nState Senate PDFs:")
for pdf_info in senate_pdfs:
    if os.path.exists(pdf_info['output']):
        size = os.path.getsize(pdf_info['output']) / 1024
        print(f"  ✓ {pdf_info['year']}: {os.path.basename(pdf_info['output'])} ({size:.1f} KB)")
