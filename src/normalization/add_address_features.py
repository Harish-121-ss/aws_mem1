from pathlib import Path
import sys

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from address_normalizer import (
    normalize_business_address,
    tokenize_address,
    extract_address_numbers,
    extract_postal_codes,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "normalized"
    / "normalized_source1.tsv"
)

TEMP_FILE = (
    PROJECT_ROOT
    / "data"
    / "normalized"
    / "normalized_source1_with_address.tmp.tsv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "normalized"
    / "normalized_source1.tsv"
)

CHUNK_SIZE = 100_000


def main():
    print("SOURCE 1 - ADDRESS FEATURE ENRICHMENT")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    if TEMP_FILE.exists():
        TEMP_FILE.unlink()

    reader = pd.read_csv(
        INPUT_FILE,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        chunksize=CHUNK_SIZE,
    )

    first_chunk = True
    total_rows = 0

    for chunk_number, chunk in enumerate(reader, start=1):

        addresses = chunk["business_address"]

        chunk["business_address_normalized"] = (
            addresses.map(normalize_business_address)
        )

        chunk["address_tokens"] = (
            addresses.map(
                lambda value: " ".join(
                    tokenize_address(value)
                )
            )
        )

        chunk["address_numbers"] = (
            addresses.map(
                lambda value: " ".join(
                    extract_address_numbers(value)
                )
            )
        )

        chunk["postal_codes"] = (
            addresses.map(
                lambda value: " ".join(
                    extract_postal_codes(value)
                )
            )
        )

        chunk.to_csv(
            TEMP_FILE,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            encoding="utf-8",
        )

        first_chunk = False
        total_rows += len(chunk)

        print(
            f"Processed chunk {chunk_number:,} "
            f"| total rows: {total_rows:,}"
        )

    # Replace the old file only after successful completion.
    INPUT_FILE.unlink()
    TEMP_FILE.replace(OUTPUT_FILE)

    print("\nAddress enrichment complete.")
    print(f"Rows processed: {total_rows:,}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()