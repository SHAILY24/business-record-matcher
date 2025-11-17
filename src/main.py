"""
Main workflow orchestration for business record matching.

Demonstrates end-to-end data cleaning, fuzzy matching, and result generation.
"""

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd

from data_cleaner import BusinessNameNormalizer, PhoneNormalizer, clean_dataframe
from fuzzy_matcher import FuzzyMatcher


def load_and_clean_csv(
    filepath: Path, column_mapping: Dict[str, str]
) -> tuple[pd.DataFrame, List[Dict]]:
    """
    Load CSV and clean data.

    Args:
        filepath: Path to CSV file
        column_mapping: Column name mapping

    Returns:
        Tuple of (original DataFrame, cleaned records)
    """
    print(f"Loading {filepath}")
    df = pd.read_csv(filepath)
    print(f"  Loaded {len(df)} records")

    print(f"Cleaning data...")
    cleaned_data = clean_dataframe(df, column_mapping)

    # Convert to list of dicts for matching
    records = []
    for i in range(len(df)):
        record = {key: cleaned_data[key][i] for key in cleaned_data.keys()}
        # Include original columns for final output
        for col in df.columns:
            if col not in record:
                record[f"original_{col}"] = df.iloc[i][col]
        records.append(record)

    return df, records


def generate_output_csv(matches: List[Dict], output_path: Path):
    """
    Generate final CSV with match results.

    Args:
        matches: List of match results
        output_path: Path for output CSV
    """
    output_records = []

    for match in matches:
        record = {
            "match_status": match["match_type"],
            "confidence_score": round(match["confidence"], 2),
            "name_similarity": round(match["name_similarity"], 2),
            "phone_match": "Yes" if match["phone_match"] else "No",
        }

        # Add source fields
        src = match["source_record"]
        for key, value in src.items():
            if key.startswith("original_"):
                record[f"source_{key.replace('original_', '')}"] = value

        # Add target fields if matched
        if match["target_record"]:
            tgt = match["target_record"]
            for key, value in tgt.items():
                if key.startswith("original_"):
                    record[f"target_{key.replace('original_', '')}"] = value
        else:
            # Fill with empty values for unmatched
            record["target_company_name"] = ""
            record["target_address"] = ""
            record["target_phone"] = ""

        output_records.append(record)

    df = pd.DataFrame(output_records)
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(output_records)} matched records to {output_path}")


def print_match_summary(summary: Dict[str, int]):
    """Print formatted match summary."""
    print("\n" + "=" * 60)
    print("MATCH SUMMARY")
    print("=" * 60)
    print(f"Total records: {summary['total']}")
    print(f"Matched: {summary['matched']} ({summary['matched']/summary['total']*100:.1f}%)")
    print(f"Unmatched: {summary['unmatched']}")
    print()
    print("Match Types:")
    print(f"  Phone matches: {summary['phone_matches']}")
    print(f"  Fuzzy name matches: {summary['fuzzy_matches']}")
    print()
    print("Confidence Distribution:")
    print(f"  High (80-100): {summary['high_confidence']}")
    print(f"  Medium (60-79): {summary['medium_confidence']}")
    print(f"  Low (<60): {summary['low_confidence']}")
    print("=" * 60)


def main():
    """Run the matching workflow."""
    parser = argparse.ArgumentParser(description="Business record fuzzy matching")
    parser.add_argument(
        "--source", type=str, default="data/input/sample_data_source1.csv", help="Source CSV file"
    )
    parser.add_argument(
        "--target", type=str, default="data/input/sample_data_source2.csv", help="Target CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/output/matched_results.csv",
        help="Output CSV file",
    )
    parser.add_argument(
        "--threshold", type=int, default=80, help="Fuzzy matching threshold (0-100)"
    )

    args = parser.parse_args()

    # Column mappings for each file
    source_mapping = {
        "normalized_name": "company_name",
        "normalized_street": "address",
        "normalized_state": "state",
        "normalized_phone": "phone",
        "original_company_name": "company_name",
        "original_address": "address",
        "original_city": "city",
        "original_state": "state",
        "original_phone": "phone",
    }

    target_mapping = {
        "normalized_name": "business_name",
        "normalized_street": "street",
        "normalized_state": "location",
        "normalized_phone": "contact_phone",
        "original_business_name": "business_name",
        "original_street": "street",
        "original_location": "location",
        "original_contact_phone": "contact_phone",
    }

    # Load and clean data
    print("\n" + "=" * 60)
    print("STEP 1: LOADING AND CLEANING DATA")
    print("=" * 60)

    source_df, source_records = load_and_clean_csv(Path(args.source), source_mapping)
    target_df, target_records = load_and_clean_csv(Path(args.target), target_mapping)

    # Show normalization examples
    print("\nNormalization Examples:")
    if source_records:
        print(f"  Source: '{source_df.iloc[0]['company_name']}'")
        print(f"    -> '{source_records[0]['normalized_name']}'")
    if target_records:
        print(f"  Target: '{target_df.iloc[0]['business_name']}'")
        print(f"    -> '{target_records[0]['normalized_name']}'")

    # Perform fuzzy matching
    print("\n" + "=" * 60)
    print("STEP 2: FUZZY MATCHING")
    print("=" * 60)
    print(f"Threshold: {args.threshold}")

    matcher = FuzzyMatcher(threshold=args.threshold)
    matches = matcher.match_records(source_records, target_records)

    # Generate summary
    summary = matcher.get_match_summary(matches)
    print_match_summary(summary)

    # Show sample matches
    print("\nSample Matches:")
    for i, match in enumerate(matches[:5], 1):
        src_name = match["source_record"].get("original_company_name", "N/A")
        if match["target_record"]:
            tgt_name = match["target_record"].get("original_business_name", "N/A")
            print(f"\n{i}. '{src_name}'")
            print(f"   -> '{tgt_name}'")
            print(f"   Confidence: {match['confidence']:.1f}%")
            print(f"   Type: {match['match_type']}")
        else:
            print(f"\n{i}. '{src_name}' -> NO MATCH")

    # Save results
    print("\n" + "=" * 60)
    print("STEP 3: GENERATING OUTPUT")
    print("=" * 60)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_output_csv(matches, output_path)

    print("\nWorkflow completed successfully!")


if __name__ == "__main__":
    main()
