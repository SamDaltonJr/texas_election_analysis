"""
Compare Political WAR to Simple vs_top_ticket Metric

Validates which metric better identifies strong candidates for statewide recruitment.
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from political_war_model import PoliticalWARModel
from district_candidate_analyzer_multiyear import MultiYearDistrictCandidateAnalyzer


def compare_metrics():
    """Compare Political WAR to simple vs_top_ticket"""

    print("="*70)
    print("Comparing Political WAR vs Simple vs_top_ticket Metric")
    print("="*70)

    # Calculate Political WAR scores
    print("\n1. Calculating Political WAR scores...")
    war_model = PoliticalWARModel()
    war_data = war_model.calculate_war_scores()

    # Calculate simple vs_top_ticket scores
    print("\n2. Calculating simple vs_top_ticket scores...")
    simple_analyzer = MultiYearDistrictCandidateAnalyzer()

    # Get all years of vs_top_ticket data
    all_years = []
    for year in [2018, 2020, 2022, 2024]:
        year_data = simple_analyzer.calculate_vs_top_ticket(year=year)
        all_years.append(year_data)

    simple_data = pd.concat(all_years, ignore_index=True)

    # Merge the two datasets
    print("\n3. Merging datasets...")

    # Create merge keys
    war_data['merge_key'] = (
        war_data['year'].astype(str) + '_' +
        war_data['district'].astype(str) + '_' +
        war_data['district_level'] + '_' +
        war_data['candidate']
    )

    simple_data['merge_key'] = (
        simple_data['year'].astype(str) + '_' +
        simple_data['district'].astype(str) + '_' +
        simple_data['district_type'] + '_' +
        simple_data['candidate']
    )

    # Merge
    comparison = war_data.merge(
        simple_data[['merge_key', 'vs_top_ticket', 'partisan_lean', 'winning_margin']],
        on='merge_key',
        how='inner',
        suffixes=('_war', '_simple')
    )

    print(f"  Matched {len(comparison):,} candidates in both datasets")

    # Calculate correlations
    print("\n" + "="*70)
    print("Correlation Analysis")
    print("="*70)

    corr_war_simple = comparison['political_war'].corr(comparison['vs_top_ticket'])
    corr_war_margin = comparison['political_war'].corr(comparison['winning_margin'])
    corr_simple_margin = comparison['vs_top_ticket'].corr(comparison['winning_margin'])

    print(f"\nPolitical WAR vs vs_top_ticket:  {corr_war_simple:.3f}")
    print(f"Political WAR vs winning_margin: {corr_war_margin:.3f}")
    print(f"vs_top_ticket vs winning_margin: {corr_simple_margin:.3f}")

    # Show cases where they disagree
    print("\n" + "="*70)
    print("Cases Where Metrics Disagree Most")
    print("="*70)

    comparison['difference'] = comparison['political_war'] - comparison['vs_top_ticket']
    disagreements = comparison.sort_values('difference', key=abs, ascending=False).head(20)

    print("\nTop 20 Disagreements:")
    print(disagreements[[
        'year', 'district', 'district_level', 'candidate', 'party',
        'political_war', 'vs_top_ticket', 'difference',
        'is_incumbent', 'partisan_lean_war'
    ]].to_string(index=False))

    # Analyze top performers by each metric
    print("\n" + "="*70)
    print("Top 10 Democrats by Political WAR vs vs_top_ticket")
    print("="*70)

    dems = comparison[comparison['party'] == 'D'].copy()

    top_war_dems = dems.nlargest(10, 'political_war')
    top_simple_dems = dems.nlargest(10, 'vs_top_ticket')

    print("\nTop 10 by Political WAR:")
    print(top_war_dems[[
        'year', 'district', 'candidate', 'political_war', 'vs_top_ticket',
        'is_incumbent', 'partisan_lean_war'
    ]].to_string(index=False))

    print("\nTop 10 by vs_top_ticket:")
    print(top_simple_dems[[
        'year', 'district', 'candidate', 'political_war', 'vs_top_ticket',
        'is_incumbent', 'partisan_lean_war'
    ]].to_string(index=False))

    # Check incumbency bias
    print("\n" + "="*70)
    print("Incumbency Bias Analysis")
    print("="*70)

    incumbent_war = comparison[comparison['is_incumbent'] == 1]['political_war'].mean()
    nonincumbent_war = comparison[comparison['is_incumbent'] == 0]['political_war'].mean()

    incumbent_simple = comparison[comparison['is_incumbent'] == 1]['vs_top_ticket'].mean()
    nonincumbent_simple = comparison[comparison['is_incumbent'] == 0]['vs_top_ticket'].mean()

    print(f"\nAverage Political WAR:")
    print(f"  Incumbents:     {incumbent_war:+.2f}")
    print(f"  Non-incumbents: {nonincumbent_war:+.2f}")
    print(f"  Difference:     {incumbent_war - nonincumbent_war:+.2f}")

    print(f"\nAverage vs_top_ticket:")
    print(f"  Incumbents:     {incumbent_simple:+.2f}")
    print(f"  Non-incumbents: {nonincumbent_simple:+.2f}")
    print(f"  Difference:     {incumbent_simple - nonincumbent_simple:+.2f}")

    print("\nInterpretation:")
    print("  Political WAR accounts for incumbency advantage in the model,")
    print("  so incumbents and non-incumbents should have similar average WAR.")
    print("  vs_top_ticket does NOT account for incumbency, so incumbents")
    print("  appear artificially stronger.")

    # Model interpretation
    print("\n" + "="*70)
    print("Model Feature Importance")
    print("="*70)
    print("\nRegression Coefficients:")
    for feature, value in war_model.feature_importance.items():
        print(f"  {feature:25s}: {value:+.3f}")

    print("\nKey Insights:")
    print(f"  - Incumbency is worth ~{war_model.feature_importance['is_incumbent']:.1f} points")
    print(f"  - Being a Democrat in Texas costs ~{abs(war_model.feature_importance['is_democrat']):.1f} points")
    print(f"  - Partisan lean has minimal direct effect (filtered through party)")
    print(f"  - Low R² (0.192) means candidate quality matters more than structural factors")

    return comparison


if __name__ == "__main__":
    comparison_df = compare_metrics()
