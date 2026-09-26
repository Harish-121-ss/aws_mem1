from pathlib import Path
from collections import Counter

from loader import (
    get_source1_chunks,
    get_source2_chunks,
    get_source3_chunks,
    get_ground_truth_chunks,
)


def validate_source(name, chunks, expected_prefix):
    print("\n" + "=" * 70)
    print(f"VALIDATING {name}")
    print("=" * 70)

    total_rows = 0
    missing_name = 0
    missing_address = 0
    missing_country = 0

    seen_ids = set()
    duplicate_ids = 0
    invalid_prefix = 0

    countries = Counter()

    for chunk in chunks:
        total_rows += len(chunk)

        missing_name += (chunk["business_name"].str.strip() == "").sum()
        missing_address += (chunk["business_address"].str.strip() == "").sum()
        missing_country += (chunk["country"].str.strip() == "").sum()

        for entity_id in chunk["entity_id"]:
            if entity_id in seen_ids:
                duplicate_ids += 1
            else:
                seen_ids.add(entity_id)

            if not entity_id.startswith(expected_prefix):
                invalid_prefix += 1

        countries.update(chunk["country"].str.strip())

    print(f"Total rows              : {total_rows:,}")
    print(f"Unique entity IDs       : {len(seen_ids):,}")
    print(f"Duplicate entity IDs    : {duplicate_ids:,}")
    print(f"Invalid ID prefixes     : {invalid_prefix:,}")
    print(f"Missing business names  : {missing_name:,}")
    print(f"Missing addresses       : {missing_address:,}")
    print(f"Missing countries       : {missing_country:,}")

    print("\nTop country values:")
    for country, count in countries.most_common(20):
        print(f"  {repr(country)} : {count:,}")

    return {
        "rows": total_rows,
        "duplicates": duplicate_ids,
        "invalid_prefix": invalid_prefix,
        "missing_name": missing_name,
        "missing_address": missing_address,
        "missing_country": missing_country,
    }


def validate_ground_truth(chunks):
    print("\n" + "=" * 70)
    print("VALIDATING GROUND TRUTH")
    print("=" * 70)

    total_rows = 0
    empty_matches = 0
    invalid_source1_ids = 0
    invalid_matched_ids = 0
    duplicate_matches = 0

    seen_source1_ids = set()

    for chunk in chunks:
        total_rows += len(chunk)

        for _, row in chunk.iterrows():
            source1_id = row["source1_entity_id"]
            matched_ids_text = row["matched_entity_ids"]

            if source1_id in seen_source1_ids:
                print(f"WARNING: duplicate Source 1 ID: {source1_id}")
            else:
                seen_source1_ids.add(source1_id)

            if not source1_id.startswith("S1-"):
                invalid_source1_ids += 1

            if not matched_ids_text.strip():
                empty_matches += 1
                continue

            matched_ids = [
                value.strip()
                for value in matched_ids_text.split(",")
                if value.strip()
            ]

            if len(matched_ids) != len(set(matched_ids)):
                duplicate_matches += 1

            for matched_id in matched_ids:
                if not (
                    matched_id.startswith("S2-")
                    or matched_id.startswith("S3-")
                ):
                    invalid_matched_ids += 1

    print(f"Total rows                  : {total_rows:,}")
    print(f"Unique Source 1 IDs         : {len(seen_source1_ids):,}")
    print(f"Empty match lists            : {empty_matches:,}")
    print(f"Invalid Source 1 IDs        : {invalid_source1_ids:,}")
    print(f"Invalid matched IDs          : {invalid_matched_ids:,}")
    print(f"Rows with duplicate matches : {duplicate_matches:,}")


def main():
    print("BUSINESS ENTITY RESOLUTION - DATA VALIDATION")

    validate_source(
        "SOURCE 1",
        get_source1_chunks(),
        "S1-",
    )

    validate_source(
        "SOURCE 2",
        get_source2_chunks(),
        "S2-",
    )

    validate_source(
        "SOURCE 3",
        get_source3_chunks(),
        "S3-",
    )

    validate_ground_truth(
        get_ground_truth_chunks()
    )

    print("\n" + "=" * 70)
    print("DATA VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()