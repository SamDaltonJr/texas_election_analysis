"""
Texas Capitol Data Portal - PDF Election Data Extractor
Extracts election results by State House district from official PDFs
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import requests
import pandas as pd
import os
import re
from pathlib import Path

class TexasElectionPDFExtractor:
    def __init__(self, output_dir="texas_election_data/pdf_extracts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Known PDF URLs from Texas Capitol Data Portal
        # These contain statewide races by State House district
        self.pdf_urls = {
            '2018_general': 'https://data.capitol.texas.gov/dataset/71af633c-21bf-42cf-ad48-4fe95593a897/resource/4391b9ea-7e1b-4872-acb4-799cb2a3d498/download/planh2316r206_18g.pdf',
            # Add more as we find them
        }

    def download_pdf(self, url, filename):
        """Download a PDF file"""
        print(f"Downloading: {filename}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"  ✓ Downloaded {len(response.content):,} bytes")
            return filepath
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None

    def install_pdf_library(self):
        """Install pdfplumber for PDF extraction"""
        print("Installing pdfplumber for PDF text extraction...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber", "-q"])
            print("  ✓ Installed pdfplumber")
            return True
        except:
            print("  ✗ Failed to install pdfplumber")
            return False

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using pdfplumber"""
        try:
            import pdfplumber
        except ImportError:
            print("pdfplumber not found. Installing...")
            if self.install_pdf_library():
                import pdfplumber
            else:
                return None

        print(f"\nExtracting text from: {os.path.basename(pdf_path)}")

        try:
            extracted_data = []

            with pdfplumber.open(pdf_path) as pdf:
                print(f"  Pages: {len(pdf.pages)}")

                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"  Processing page {page_num}/{len(pdf.pages)}...", end='\r')

                    # Extract text
                    text = page.extract_text()

                    # Try to extract tables (more structured)
                    tables = page.extract_tables()

                    if tables:
                        for table in tables:
                            extracted_data.append({
                                'page': page_num,
                                'type': 'table',
                                'data': table
                            })

                    if text:
                        extracted_data.append({
                            'page': page_num,
                            'type': 'text',
                            'data': text
                        })

                print(f"\n  ✓ Extracted {len(extracted_data)} data segments")
                return extracted_data

        except Exception as e:
            print(f"\n  ✗ Error: {e}")
            return None

    def parse_election_tables(self, extracted_data, year):
        """Parse extracted tables into structured election data"""
        print(f"\nParsing election data for {year}...")

        all_results = []

        for segment in extracted_data:
            if segment['type'] == 'table':
                table = segment['data']

                # Try to identify if this is an election results table
                # Look for patterns like district numbers, candidate names, vote totals

                for row in table:
                    if row and len(row) > 2:
                        # Check if this looks like a data row
                        # Example: ['1', 'Candidate Name', '12,345', '56.7%']

                        # Try to extract district (usually first column)
                        district = None
                        if row[0] and str(row[0]).strip().isdigit():
                            district = int(row[0])

                        # This is a simplified parser - would need to be adjusted
                        # based on actual PDF structure
                        if district:
                            result = {
                                'year': year,
                                'district': district,
                                'page': segment['page'],
                                'raw_row': row
                            }
                            all_results.append(result)

        print(f"  Found {len(all_results)} potential data rows")
        return all_results

    def convert_to_dataframe(self, parsed_data):
        """Convert parsed data to pandas DataFrame"""
        if not parsed_data:
            return None

        df = pd.DataFrame(parsed_data)
        return df

    def process_pdf(self, url, year, save_csv=True):
        """Main processing pipeline for a single PDF"""
        print(f"\n{'='*60}")
        print(f"Processing {year} Election Data")
        print(f"{'='*60}")

        # Download PDF
        filename = f"texas_election_{year}.pdf"
        pdf_path = self.download_pdf(url, filename)

        if not pdf_path:
            return None

        # Extract text/tables
        extracted = self.extract_text_from_pdf(pdf_path)

        if not extracted:
            return None

        # Save raw extraction for manual review
        raw_output = os.path.join(self.output_dir, f"raw_extract_{year}.txt")
        with open(raw_output, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(extracted):
                f.write(f"\n{'='*60}\n")
                f.write(f"Page {segment['page']} - {segment['type'].upper()}\n")
                f.write(f"{'='*60}\n")

                if segment['type'] == 'table':
                    for row in segment['data']:
                        f.write(f"{row}\n")
                else:
                    f.write(segment['data'])
                f.write("\n")

        print(f"  ✓ Saved raw extraction to: {os.path.basename(raw_output)}")

        # Parse into structured data
        parsed = self.parse_election_tables(extracted, year)

        # Convert to DataFrame
        df = self.convert_to_dataframe(parsed)

        if df is not None and save_csv:
            csv_path = os.path.join(self.output_dir, f"parsed_{year}.csv")
            df.to_csv(csv_path, index=False)
            print(f"  ✓ Saved parsed data to: {os.path.basename(csv_path)}")

        return df

    def process_all(self):
        """Process all known PDFs"""
        print("="*60)
        print("TEXAS ELECTION PDF EXTRACTOR")
        print("="*60)

        results = {}

        for key, url in self.pdf_urls.items():
            year = key.split('_')[0]
            df = self.process_pdf(url, year)
            if df is not None:
                results[key] = df

        print(f"\n{'='*60}")
        print("EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"Successfully processed {len(results)} PDFs")
        print(f"Output directory: {os.path.abspath(self.output_dir)}")

        return results

def main():
    extractor = TexasElectionPDFExtractor()

    # Process the 2018 general election PDF
    results = extractor.process_all()

    # Print instructions for manual review
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}")
    print("1. Review the raw_extract_*.txt files to understand the PDF structure")
    print("2. The PDF likely contains tables with:")
    print("   - State House District numbers (1-150)")
    print("   - Statewide races (Governor, Senate, etc.)")
    print("   - Vote totals by candidate per district")
    print("3. Once we understand the structure, we can write a custom parser")
    print("4. Look for similar PDFs for other years on:")
    print("   https://data.capitol.texas.gov/")

if __name__ == "__main__":
    main()
