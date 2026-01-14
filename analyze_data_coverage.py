"""
Texas Election Data Coverage Analysis
Generates a comprehensive report of available election data for modeling
"""

import pandas as pd
import os
from pathlib import Path
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class DataCoverageAnalyzer:
    def __init__(self, base_dir="texas_election_data"):
        self.base_dir = base_dir
        self.clean_dir = os.path.join(base_dir, "clean")
        self.raw_dir = os.path.join(base_dir, "raw")

    def analyze_file(self, filepath):
        """Analyze a single data file and return metadata"""
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()

        result = {
            'filename': filename,
            'path': filepath,
            'size_kb': os.path.getsize(filepath) / 1024,
            'type': ext,
            'rows': 0,
            'columns': 0,
            'column_names': [],
            'years_covered': [],
            'offices': [],
            'usable': False,
            'issues': []
        }

        try:
            # Try to load as DataFrame
            if ext == '.csv':
                # Check if it's actually HTML
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('<!'):
                        result['issues'].append('File is HTML, not CSV')
                        result['usable'] = False
                        return result

                df = pd.read_csv(filepath, low_memory=False)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif ext == '.tsv':
                df = pd.read_csv(filepath, sep='\t', low_memory=False)
            else:
                result['issues'].append(f'Unsupported file type: {ext}')
                return result

            # Extract metadata
            result['rows'] = len(df)
            result['columns'] = len(df.columns)
            result['column_names'] = list(df.columns)
            result['usable'] = True

            # Try to identify years
            if 'year' in df.columns:
                result['years_covered'] = sorted(df['year'].dropna().unique().tolist())
            elif any('year' in str(col).lower() for col in df.columns):
                year_col = [col for col in df.columns if 'year' in str(col).lower()][0]
                result['years_covered'] = sorted(df[year_col].dropna().unique().tolist())

            # Try to identify offices/races
            if 'office' in df.columns:
                result['offices'] = df['office'].dropna().unique().tolist()[:20]  # Limit to first 20
            elif any('office' in str(col).lower() for col in df.columns):
                office_col = [col for col in df.columns if 'office' in str(col).lower()][0]
                result['offices'] = df[office_col].dropna().unique().tolist()[:20]

            # Check data quality
            if result['rows'] == 0:
                result['issues'].append('File is empty')
                result['usable'] = False
            elif result['rows'] < 10:
                result['issues'].append(f'Very few rows ({result["rows"]})')

        except Exception as e:
            result['issues'].append(f'Error reading file: {str(e)}')
            result['usable'] = False

        return result

    def scan_directory(self):
        """Scan all data directories and analyze files"""
        all_files = []

        # Scan clean directory
        if os.path.exists(self.clean_dir):
            for file in os.listdir(self.clean_dir):
                filepath = os.path.join(self.clean_dir, file)
                if os.path.isfile(filepath) and file.endswith(('.csv', '.xlsx', '.xls', '.tsv')):
                    all_files.append(filepath)

        # Scan raw directory
        if os.path.exists(self.raw_dir):
            for file in os.listdir(self.raw_dir):
                filepath = os.path.join(self.raw_dir, file)
                if os.path.isfile(filepath) and file.endswith(('.csv', '.xlsx', '.xls', '.tsv')):
                    all_files.append(filepath)

        # Scan base directory
        if os.path.exists(self.base_dir):
            for file in os.listdir(self.base_dir):
                filepath = os.path.join(self.base_dir, file)
                if os.path.isfile(filepath) and file.endswith(('.csv', '.xlsx', '.xls', '.tsv')):
                    all_files.append(filepath)

        print(f"Found {len(all_files)} data files to analyze...\n")

        results = []
        for filepath in all_files:
            print(f"Analyzing: {os.path.basename(filepath)}...")
            result = self.analyze_file(filepath)
            results.append(result)

        return results

    def generate_report(self, results):
        """Generate a comprehensive coverage report"""

        print("\n" + "="*80)
        print("TEXAS ELECTION DATA COVERAGE REPORT")
        print("="*80)

        # Separate usable from non-usable files
        usable = [r for r in results if r['usable']]
        non_usable = [r for r in results if not r['usable']]

        print(f"\n📊 SUMMARY")
        print(f"   Total files scanned: {len(results)}")
        print(f"   ✓ Usable files: {len(usable)}")
        print(f"   ✗ Non-usable files: {len(non_usable)}")

        # Analyze usable data
        if usable:
            total_rows = sum(r['rows'] for r in usable)
            all_years = set()
            all_offices = set()

            for r in usable:
                all_years.update(r['years_covered'])
                all_offices.update(r['offices'])

            print(f"\n   Total usable records: {total_rows:,}")
            print(f"   Years with data: {sorted(all_years) if all_years else 'Unknown'}")
            print(f"   Unique offices/races: {len(all_offices)}")

        # Detailed breakdown of usable files
        print(f"\n{'='*80}")
        print("✓ USABLE DATA FILES")
        print(f"{'='*80}\n")

        for i, r in enumerate(usable, 1):
            print(f"{i}. {r['filename']}")
            print(f"   Location: {os.path.dirname(r['path'])}")
            print(f"   Size: {r['size_kb']:.1f} KB")
            print(f"   Dimensions: {r['rows']:,} rows × {r['columns']} columns")

            if r['years_covered']:
                print(f"   Years: {', '.join(map(str, sorted(r['years_covered'])))}")

            if r['offices']:
                offices_display = r['offices'][:5]  # Show first 5
                print(f"   Sample offices: {', '.join(offices_display)}")
                if len(r['offices']) > 5:
                    print(f"   ... and {len(r['offices']) - 5} more")

            print(f"   Columns: {', '.join(r['column_names'][:8])}")
            if len(r['column_names']) > 8:
                print(f"            ... and {len(r['column_names']) - 8} more")

            print()

        # Non-usable files
        if non_usable:
            print(f"\n{'='*80}")
            print("✗ NON-USABLE FILES (Need Fixing)")
            print(f"{'='*80}\n")

            for i, r in enumerate(non_usable, 1):
                print(f"{i}. {r['filename']}")
                print(f"   Location: {os.path.dirname(r['path'])}")
                print(f"   Issues: {', '.join(r['issues'])}")
                print()

        # Coverage gaps
        print(f"\n{'='*80}")
        print("📅 DATA COVERAGE BY YEAR")
        print(f"{'='*80}\n")

        year_coverage = {}
        for r in usable:
            for year in r['years_covered']:
                if year not in year_coverage:
                    year_coverage[year] = []
                year_coverage[year].append(r['filename'])

        if year_coverage:
            for year in sorted(year_coverage.keys()):
                print(f"{year}:")
                for filename in year_coverage[year]:
                    print(f"   ✓ {filename}")
            print()

            # Identify gaps
            if year_coverage:
                min_year = min(year_coverage.keys())
                max_year = max(year_coverage.keys())
                all_years_range = set(range(int(min_year), int(max_year) + 1))
                missing_years = all_years_range - set(year_coverage.keys())

                if missing_years:
                    print(f"⚠ Missing data for years: {sorted(missing_years)}")
                else:
                    print(f"✓ Complete coverage from {min_year} to {max_year}")
        else:
            print("⚠ No year information available in files")

        # Recommendations
        print(f"\n{'='*80}")
        print("💡 RECOMMENDATIONS")
        print(f"{'='*80}\n")

        if non_usable:
            print("1. FIX NON-USABLE FILES:")
            for r in non_usable:
                if 'HTML' in str(r['issues']):
                    print(f"   • {r['filename']}: Download proper CSV/Excel from source")

        if year_coverage:
            missing_years = set(range(2014, 2025)) - set(year_coverage.keys())
            if missing_years:
                print(f"\n2. FILL DATA GAPS:")
                print(f"   Missing years: {sorted(missing_years)}")
                print(f"   Sources:")
                print(f"   • Texas SOS: https://www.sos.state.tx.us/elections/historical/")
                print(f"   • OpenElections: https://github.com/openelections/openelections-data-tx")
                print(f"   • MIT Election Lab: https://dataverse.harvard.edu")

        print(f"\n3. DATA QUALITY:")
        print(f"   • Verify all files have consistent column names")
        print(f"   • Check for missing values in key columns (year, county, votes)")
        print(f"   • Standardize party names (DEM vs Democrat, REP vs Republican)")

        print(f"\n4. READY FOR MODELING:")
        if len(usable) >= 3:
            print(f"   ✓ You have sufficient data to begin modeling!")
            print(f"   • Focus on years with complete coverage")
            print(f"   • Start with county-level aggregation")
            print(f"   • Use precinct-level data for detailed analysis")
        else:
            print(f"   ⚠ Limited data available - consider downloading more sources")

        print(f"\n{'='*80}\n")

        # Save report to file
        report_file = os.path.join(self.base_dir, "DATA_COVERAGE_REPORT.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            # Write summary
            f.write("="*80 + "\n")
            f.write("TEXAS ELECTION DATA COVERAGE REPORT\n")
            f.write("="*80 + "\n\n")

            f.write("USABLE DATA FILES:\n")
            f.write("-"*80 + "\n")
            for r in usable:
                f.write(f"\n{r['filename']}\n")
                f.write(f"  Rows: {r['rows']:,} | Columns: {r['columns']}\n")
                if r['years_covered']:
                    f.write(f"  Years: {', '.join(map(str, sorted(r['years_covered'])))}\n")
                f.write(f"  Columns: {', '.join(r['column_names'])}\n")

            f.write("\n" + "="*80 + "\n")
            f.write("NON-USABLE FILES:\n")
            f.write("-"*80 + "\n")
            for r in non_usable:
                f.write(f"\n{r['filename']}\n")
                f.write(f"  Issues: {', '.join(r['issues'])}\n")

        print(f"📄 Full report saved to: {report_file}")

        return usable, non_usable

def main():
    analyzer = DataCoverageAnalyzer()
    results = analyzer.scan_directory()
    usable, non_usable = analyzer.generate_report(results)

if __name__ == "__main__":
    main()
