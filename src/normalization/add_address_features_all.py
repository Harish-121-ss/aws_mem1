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
NORMALIZED_DIR = PROJECT_ROOT / "data" / "normalized"

FILES = [
    "normalized_source2.tsv",
    "normalized_source3.tsv",
]

CHUNK_SIZE = 100_000


def enrich_file(filename: str) -> None:
    input_file = NORMALIZED_DIR / filename
    temp_file = NORMALIZED_DIR / f"{filename}.tmp"

    print("\n" + "=" * 70)
    print(f"PROCESSING: {filename}")
    print("=" * 70)

    if not input_file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")

    if temp_file.exists():
        temp_file.unlink()

    reader = pd.read_csv(
        input_file,
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
            temp_file,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            encoding="utf-8",
        )

        first_chunk = False
        total_rows += len(chunk)

        print(
            f"Chunk {chunk_number:,} "
            f"| rows processed: {total_rows:,}"
        )

    input_file.unlink()
    temp_file.replace(input_file)

    print(f"\nCompleted: {filename}")
    print(f"Rows processed: {total_rows:,}")


def main():
    print("MEMBER 1 - SOURCE 2/3 ADDRESS ENRICHMENT")

    for filename in FILES:
        enrich_file(filename)

    print("\n" + "=" * 70)
    print("SOURCE 2/3 ADDRESS ENRICHMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()