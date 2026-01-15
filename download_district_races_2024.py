"""
Download 2024 District Race PDFs (Red-226 Reports)

Downloads r8.pdf files containing actual district race results:
- State House Districts 1-150 (actual State Rep races)
- State Senate Districts 1-31 (actual State Senate races)

These are Red-226 "District Election Reports" showing the races FOR those districts,
not Red-206 reports showing statewide races broken down BY district.
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import requests
import os
import time

# Create output directories
house_dir = "texas_election_data/district_races/house_2024"
senate_dir = "texas_election_data/district_races/senate_2024"
os.makedirs(house_dir, exist_ok=True)
os.makedirs(senate_dir, exist_ok=True)

def download_pdf(url, output_path, district_type, district_num):
    """Download a single PDF file"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {district_type} District {district_num}")
            return True
        else:
            print(f"✗ Failed {district_type} District {district_num}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error {district_type} District {district_num}: {str(e)}")
        return False

print("="*70)
print("Downloading 2024 District Race Reports (Red-226)")
print("="*70)

# Download State House districts (1-150)
print("\n" + "="*70)
print("STATE HOUSE DISTRICTS (1-150)")
print("="*70)

house_success = 0
house_failed = 0

for i in range(1, 151):
    url = f"https://wrm.capitol.texas.gov/fyiwebdocs/PDF/house/dist{i}/r8.pdf"
    output_path = f"{house_dir}/house_dist_{i:03d}_2024.pdf"

    if download_pdf(url, output_path, "House", i):
        house_success += 1
    else:
        house_failed += 1

    # Be polite to the server
    time.sleep(0.5)

print(f"\nHouse Districts: {house_success} downloaded, {house_failed} failed")

# Download State Senate districts (1-31)
print("\n" + "="*70)
print("STATE SENATE DISTRICTS (1-31)")
print("="*70)

senate_success = 0
senate_failed = 0

for i in range(1, 32):
    url = f"https://wrm.capitol.texas.gov/fyiwebdocs/PDF/senate/dist{i}/r8.pdf"
    output_path = f"{senate_dir}/senate_dist_{i:02d}_2024.pdf"

    if download_pdf(url, output_path, "Senate", i):
        senate_success += 1
    else:
        senate_failed += 1

    # Be polite to the server
    time.sleep(0.5)

print(f"\nSenate Districts: {senate_success} downloaded, {senate_failed} failed")

# Summary
print("\n" + "="*70)
print("DOWNLOAD COMPLETE")
print("="*70)
print(f"Total State House PDFs: {house_success}/{150}")
print(f"Total State Senate PDFs: {senate_success}/{31}")
print(f"\nFiles saved to:")
print(f"  - {house_dir}/")
print(f"  - {senate_dir}/")
