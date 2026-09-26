from pathlib import Path
import sys

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from name_normalizer import (
    normalize_business_name,
    tokenize_business_name,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "dataset" / "train"
OUTPUT_DIR = PROJECT_ROOT / "data" / "normalized"

SOURCE_FILES = {
    "source1": "train_source1.tsv",
    "source2": "train_source2.tsv",
    "source3": "train_source3.tsv",
}

CHUNK_SIZE = 100_000


def normalize_file(source_name: str, filename: str) -> None:
    input_path = INPUT_DIR / filename
    output_path = OUTPUT_DIR / f"normalized_{source_name}.tsv"

    print("\n" + "=" * 70)
    print(f"PROCESSING {source_name.upper()}")
    print("=" * 70)

    print(f"Input : {input_path}")
    print(f"Output: {output_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        output_path.unlink()

    reader = pd.read_csv(
        input_path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        chunksize=CHUNK_SIZE,
    )

    first_chunk = True
    total_rows = 0

    for chunk_number, chunk in enumerate(reader, start=1):

        chunk["business_name_normalized"] = (
            chunk["business_name"].map(normalize_business_name)
        )

        chunk["business_name_tokens"] = (
            chunk["business_name"].map(
                lambda value: " ".join(
                    tokenize_business_name(value)
                )
            )
        )

        chunk.to_csv(
            output_path,
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

    print(f"\nCompleted {source_name}")
    print(f"Total rows: {total_rows:,}")
    print(f"Saved to : {output_path}")


def main() -> None:
    print("MEMBER 1 - BUSINESS NAME NORMALIZATION")
    print("=" * 70)

    for source_name, filename in SOURCE_FILES.items():
        normalize_file(source_name, filename)

    print("\n" + "=" * 70)
    print("NAME NORMALIZATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()