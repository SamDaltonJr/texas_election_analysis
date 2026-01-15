"""
Texas Election Results Scraper for 2020-2024
Scrapes data from Texas Secretary of State election results website
"""

import requests
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class TexasElectionScraper:
    def __init__(self, output_dir="texas_election_data"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_results_portal(self, year):
        """
        Scrape data from the Texas election results portal
        URL pattern: https://results.texas-election.com/races?year=YYYY
        """

        print(f"\n{'='*60}")
        print(f"Scraping {year} Election Results")
        print(f"{'='*60}")

        # The Texas election results portal uses an API endpoint
        api_base = "https://results.texas-election.com/api"

        # Try to get the election data
        results = []

        try:
            # Step 1: Get list of races
            print(f"Fetching race list for {year}...")
            races_url = f"{api_base}/races"
            params = {'year': year, 'type': 'general'}

            response = self.session.get(races_url, params=params, timeout=30)

            if response.status_code == 200:
                try:
                    races = response.json()
                    print(f"  Found {len(races)} races")

                    # Step 2: Get results for each race
                    for i, race in enumerate(races[:5], 1):  # Start with first 5 races
                        print(f"  Fetching race {i}/{min(5, len(races))}: {race.get('name', 'Unknown')}")
                        race_id = race.get('id')

                        if race_id:
                            race_url = f"{api_base}/races/{race_id}/results"
                            race_response = self.session.get(race_url, timeout=30)

                            if race_response.status_code == 200:
                                race_data = race_response.json()
                                results.append({
                                    'year': year,
                                    'race': race.get('name'),
                                    'office': race.get('office'),
                                    'data': race_data
                                })

                        time.sleep(0.5)  # Be respectful

                except json.JSONDecodeError:
                    print(f"  Could not parse JSON response")
            else:
                print(f"  Failed to fetch races (Status: {response.status_code})")

        except Exception as e:
            print(f"  Error: {e}")

        return results

    def scrape_county_csv_export(self, year):
        """
        Try to download the county-level CSV export if available
        """
        print(f"\nAttempting to download {year} county-level CSV export...")

        # Known export URLs from the results portal
        export_url = f"https://results.texas-election.com/static/exports/{year}GE/county.csv"

        try:
            response = self.session.get(export_url, timeout=30)

            if response.status_code == 200:
                # Save the raw content
                filename = f"tx_{year}_general_raw.csv"
                filepath = os.path.join(self.output_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"  ✓ Downloaded raw file: {filename}")

                # Try to parse it
                # The file might be a CSV-like format that needs special parsing
                lines = response.text.split('\n')

                print(f"  File contains {len(lines)} lines")
                print(f"  First few lines:")
                for line in lines[:10]:
                    print(f"    {line[:100]}")

                # Check if it's actually HTML
                if response.text.strip().startswith('<!'):
                    print(f"  ⚠ File is HTML, not CSV. Website may require JavaScript.")
                    return None

                # Try parsing as CSV with different approaches
                try:
                    # Approach 1: Standard CSV
                    df = pd.read_csv(filepath)
                    print(f"  ✓ Parsed as CSV: {len(df)} rows, {len(df.columns)} columns")
                    return df
                except Exception as e:
                    print(f"  ✗ Standard CSV parse failed: {e}")

                    # Approach 2: Try with different delimiters
                    try:
                        df = pd.read_csv(filepath, sep='\t')
                        print(f"  ✓ Parsed as TSV: {len(df)} rows, {len(df.columns)} columns")
                        return df
                    except:
                        print(f"  ✗ Could not parse file as structured data")
                        return None
            else:
                print(f"  ✗ Download failed (Status {response.status_code})")
                return None

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None

    def scrape_sos_historical_page(self, year):
        """
        Scrape the Texas Secretary of State historical results page
        """
        print(f"\nScraping Texas SOS historical page for {year}...")

        base_url = "https://www.sos.state.tx.us/elections/historical"
        page_url = f"{base_url}/{year}.shtml"

        try:
            response = self.session.get(page_url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for downloadable files (Excel, CSV, PDF)
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    text = a.get_text(strip=True)

                    if any(ext in href.lower() for ext in ['.xls', '.xlsx', '.csv', '.pdf']):
                        full_url = href if href.startswith('http') else f"https://www.sos.state.tx.us{href}"
                        links.append({
                            'text': text,
                            'url': full_url,
                            'type': href.split('.')[-1].lower()
                        })

                if links:
                    print(f"  Found {len(links)} downloadable files:")
                    for link in links[:10]:
                        print(f"    - [{link['type'].upper()}] {link['text'][:60]}")

                    return links
                else:
                    print(f"  No downloadable files found")
                    return []
            else:
                print(f"  ✗ Failed to load page (Status {response.status_code})")
                return []

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []

    def download_file_from_link(self, url, filename):
        """Download a file from a direct URL"""
        try:
            response = self.session.get(url, timeout=60)

            if response.status_code == 200:
                filepath = os.path.join(self.output_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"  ✓ Downloaded: {filename}")

                # Try to parse if it's a structured file
                if filename.endswith('.csv'):
                    try:
                        df = pd.read_csv(filepath)
                        print(f"    Parsed: {len(df)} rows × {len(df.columns)} columns")
                        return df
                    except:
                        pass
                elif filename.endswith(('.xls', '.xlsx')):
                    try:
                        df = pd.read_excel(filepath)
                        print(f"    Parsed: {len(df)} rows × {len(df.columns)} columns")
                        return df
                    except:
                        pass

                return True
            else:
                print(f"  ✗ Download failed (Status {response.status_code})")
                return None

        except Exception as e:
            print(f"  ✗ Error downloading: {e}")
            return None

    def scrape_all_years(self, years=[2020, 2022, 2024]):
        """Main method to scrape all specified years"""

        print("="*60)
        print("TEXAS ELECTION DATA SCRAPER")
        print("="*60)
        print(f"Target years: {years}")
        print(f"Output directory: {self.output_dir}")

        os.makedirs(self.output_dir, exist_ok=True)

        all_results = {}

        for year in years:
            year_results = {
                'year': year,
                'county_csv': None,
                'sos_links': [],
                'downloaded_files': []
            }

            # Approach 1: Try county CSV export
            df = self.scrape_county_csv_export(year)
            if df is not None and len(df) > 0:
                year_results['county_csv'] = df

            # Approach 2: Check SOS historical page for download links
            links = self.scrape_sos_historical_page(year)
            year_results['sos_links'] = links

            # Try downloading some of the linked files
            if links:
                print(f"\n  Attempting to download files from SOS page...")
                for link in links[:3]:  # Download first 3 files
                    safe_name = f"{year}_{link['text'][:30].replace(' ', '_')}.{link['type']}"
                    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('_', '.', '-'))

                    result = self.download_file_from_link(link['url'], safe_name)
                    if result is not None:
                        year_results['downloaded_files'].append({
                            'filename': safe_name,
                            'original_url': link['url']
                        })

            all_results[year] = year_results

            # Be respectful - pause between years
            if year != years[-1]:
                time.sleep(2)

        return all_results

def main():
    scraper = TexasElectionScraper()
    results = scraper.scrape_all_years([2020, 2022, 2024])

    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)

    for year, data in results.items():
        print(f"\n{year}:")
        if data['county_csv'] is not None:
            print(f"  ✓ County CSV data: {len(data['county_csv'])} rows")
        else:
            print(f"  ✗ County CSV data: Not available")

        print(f"  Found {len(data['sos_links'])} links on SOS page")
        print(f"  Downloaded {len(data['downloaded_files'])} files")

    print(f"\n✓ All files saved to: {os.path.abspath(scraper.output_dir)}")

    # Save a summary
    summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'years_scraped': list(results.keys()),
        'total_files_downloaded': sum(len(r['downloaded_files']) for r in results.values())
    }

    summary_file = os.path.join(scraper.output_dir, 'scrape_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
