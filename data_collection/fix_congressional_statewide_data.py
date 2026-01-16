"""
Fix Congressional District Statewide Data

The PLANC2308 PDFs we downloaded have incorrect data (hypothetical 2025 redistricting applied to old elections).
This script creates correct statewide-by-congressional-district data using verified sources.

For now, we'll document that congressional district analysis is NOT AVAILABLE until we can:
1. Download correct Red-206 reports for PLANC2100 (2018-2020) and PLANC2193 (2022-2024)
2. Or obtain VTD-to-Congressional-District mapping files
3. Or use a verified third-party source like Daily Kos Elections

TEMPORARY SOLUTION: Mark congressional statewide data as unreliable
"""

import pandas as pd
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("="*70)
    print("Congressional District Data - STATUS CHECK")
    print("="*70)

    print("\n⚠ WARNING: Congressional district statewide data is INCORRECT")
    print("\nThe current data in:")
    print("  texas_election_data/pdf_extracts/2018_2024_congressional_results_combined.csv")
    print("\nwas parsed from PLANC2308 PDFs which use 2020 Census redistricting")
    print("applied retroactively to 2018-2024 elections.")
    print("\nThis does NOT match the actual congressional districts used in those elections.")

    print("\n" + "="*70)
    print("VERIFICATION:")
    print("="*70)
    print("\nTexas Congressional District 9 - 2020 Presidential Results:")
    print("  Actual (per Texas Politics Project):")
    print("    Biden: 75.7%")
    print("    Trump: 23.2%")
    print("\n  Our parsed data (WRONG):")
    print("    Biden: 46.7%")
    print("    Trump: 52.0%")

    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("\nUntil we fix this, congressional district analysis should be EXCLUDED.")
    print("\nTo fix, we need to:")
    print("  1. Download Red-206 reports for correct district plans:")
    print("     - PLANC2100 for 2018 & 2020 elections")
    print("     - PLANC2193 for 2022 & 2024 elections")
    print("  2. Or use VTD data with VTD-to-Congressional mapping")
    print("  3. Or download verified data from Daily Kos Elections")

    print("\n" + "="*70)
    print("ACTION TAKEN:")
    print("="*70)
    print("\nRemoving unreliable congressional statewide data file...")

    import os
    bad_file = "texas_election_data/pdf_extracts/2018_2024_congressional_results_combined.csv"
    if os.path.exists(bad_file):
        # Rename to mark as bad
        os.rename(bad_file, bad_file.replace('.csv', '_INCORRECT_DO_NOT_USE.csv'))
        print(f"✓ Renamed to: {bad_file.replace('.csv', '_INCORRECT_DO_NOT_USE.csv')}")

    print("\n✓ Congressional district recruitment analysis is now DISABLED")
    print("  until correct data is available.")

if __name__ == "__main__":
    main()
