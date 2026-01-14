"""
Texas Election Results Data Collector
Fetches statewide and legislative election results from 2014-2024
Outputs data in CSV format

Data sources:
- Texas Secretary of State: elections.sos.state.tx.us
- Texas Capitol Data Portal: data.capitol.texas.gov
"""

import requests
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time

class TexasElectionCollector:
    def __init__(self, output_dir="election_data"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        os.makedirs(output_dir, exist_ok=True)

    def collect_all_data(self):
        """Main method to collect all election data"""
        print("Starting Texas election data collection...")
        print("=" * 60)

        # Collect different types of elections
        results = {
            'statewide': self.collect_statewide_results(),
            'congressional': self.collect_congressional_results(),
            'state_senate': self.collect_state_senate_results(),
            'state_house': self.collect_state_house_results()
        }

        # Save to CSV files
        self.save_to_csv(results)

        print("\n" + "=" * 60)
        print("Data collection complete!")
        print(f"Files saved to: {self.output_dir}/")

        return results

    def collect_statewide_results(self):
        """Collect statewide election results (President, Governor, Senate, etc.)"""
        print("\n1. Collecting statewide election results...")

        results = []

        # Election years from 2014-2024
        election_years = [2014, 2016, 2018, 2020, 2022, 2024]

        # Statewide offices
        offices = [
            'President',
            'U.S. Senate',
            'Governor',
            'Lieutenant Governor',
            'Attorney General',
            'Comptroller',
            'Commissioner of the General Land Office',
            'Commissioner of Agriculture',
            'Railroad Commissioner'
        ]

        for year in election_years:
            print(f"  Processing {year}...")

            # Try to fetch from Texas SOS
            url = f"https://elections.sos.state.tx.us/index.htm"

            try:
                # Note: This is a placeholder structure
                # Real implementation would need to scrape or use available data sources
                for office in offices:
                    # Skip offices not on ballot that year
                    if office == 'President' and year % 4 != 0:
                        continue
                    if office == 'U.S. Senate' and year not in [2014, 2018, 2020, 2024]:
                        continue

                    result = {
                        'year': year,
                        'office': office,
                        'candidate': 'Data to be fetched',
                        'party': 'Data to be fetched',
                        'votes': 0,
                        'percentage': 0.0,
                        'source_url': url
                    }
                    results.append(result)

                time.sleep(0.5)  # Be respectful to servers

            except Exception as e:
                print(f"    Error processing {year}: {e}")

        print(f"  Collected {len(results)} statewide race records (placeholders)")
        return results

    def collect_congressional_results(self):
        """Collect U.S. Congressional race results"""
        print("\n2. Collecting U.S. Congressional results...")

        results = []
        election_years = [2014, 2016, 2018, 2020, 2022, 2024]

        # Texas has 38 congressional districts (as of 2022 redistricting)
        for year in election_years:
            print(f"  Processing {year}...")

            # Determine number of districts for that year
            num_districts = 36 if year < 2022 else 38

            for district in range(1, num_districts + 1):
                result = {
                    'year': year,
                    'office': 'U.S. House',
                    'district': district,
                    'candidate': 'Data to be fetched',
                    'party': 'Data to be fetched',
                    'votes': 0,
                    'percentage': 0.0,
                    'incumbent': False
                }
                results.append(result)

        print(f"  Collected {len(results)} Congressional race records (placeholders)")
        return results

    def collect_state_senate_results(self):
        """Collect Texas State Senate race results"""
        print("\n3. Collecting State Senate results...")

        results = []
        election_years = [2014, 2016, 2018, 2020, 2022, 2024]

        # Texas has 31 state senate districts
        for year in election_years:
            print(f"  Processing {year}...")

            for district in range(1, 32):
                result = {
                    'year': year,
                    'office': 'State Senate',
                    'district': district,
                    'candidate': 'Data to be fetched',
                    'party': 'Data to be fetched',
                    'votes': 0,
                    'percentage': 0.0
                }
                results.append(result)

        print(f"  Collected {len(results)} State Senate race records (placeholders)")
        return results

    def collect_state_house_results(self):
        """Collect Texas State House race results"""
        print("\n4. Collecting State House results...")

        results = []
        election_years = [2014, 2016, 2018, 2020, 2022, 2024]

        # Texas has 150 state house districts
        for year in election_years:
            print(f"  Processing {year}...")

            for district in range(1, 151):
                result = {
                    'year': year,
                    'office': 'State House',
                    'district': district,
                    'candidate': 'Data to be fetched',
                    'party': 'Data to be fetched',
                    'votes': 0,
                    'percentage': 0.0
                }
                results.append(result)

        print(f"  Collected {len(results)} State House race records (placeholders)")
        return results

    def save_to_csv(self, results):
        """Save collected results to CSV files"""
        print("\n5. Saving data to CSV files...")

        # Save statewide results
        if results['statewide']:
            filename = os.path.join(self.output_dir, 'texas_statewide_results.csv')
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if results['statewide']:
                    writer = csv.DictWriter(f, fieldnames=results['statewide'][0].keys())
                    writer.writeheader()
                    writer.writerows(results['statewide'])
            print(f"  Saved: texas_statewide_results.csv")

        # Save congressional results
        if results['congressional']:
            filename = os.path.join(self.output_dir, 'texas_congressional_results.csv')
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if results['congressional']:
                    writer = csv.DictWriter(f, fieldnames=results['congressional'][0].keys())
                    writer.writeheader()
                    writer.writerows(results['congressional'])
            print(f"  Saved: texas_congressional_results.csv")

        # Save state senate results
        if results['state_senate']:
            filename = os.path.join(self.output_dir, 'texas_state_senate_results.csv')
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if results['state_senate']:
                    writer = csv.DictWriter(f, fieldnames=results['state_senate'][0].keys())
                    writer.writeheader()
                    writer.writerows(results['state_senate'])
            print(f"  Saved: texas_state_senate_results.csv")

        # Save state house results
        if results['state_house']:
            filename = os.path.join(self.output_dir, 'texas_state_house_results.csv')
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if results['state_house']:
                    writer = csv.DictWriter(f, fieldnames=results['state_house'][0].keys())
                    writer.writeheader()
                    writer.writerows(results['state_house'])
            print(f"  Saved: texas_state_house_results.csv")

def main():
    print("Texas Election Results Data Collector")
    print("Period: 2014-2024")
    print("=" * 60)

    collector = TexasElectionCollector()
    collector.collect_all_data()

    print("\nNOTE: This script creates the framework and placeholder data.")
    print("To fetch actual election results, you'll need to:")
    print("1. Access the Texas Secretary of State historical data pages")
    print("2. Download data from data.capitol.texas.gov")
    print("3. Or scrape from elections.sos.state.tx.us")
    print("\nSee README for manual download instructions.")

if __name__ == "__main__":
    main()
