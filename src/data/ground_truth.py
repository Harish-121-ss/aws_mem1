from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "dataset"
    / "train"
    / "train_ground_truth.tsv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "ground_truth"

OUTPUT_FILE = OUTPUT_DIR / "ground_truth_parsed.tsv"

CHUNK_SIZE = 100_000


EXPECTED_COLUMNS = [
    "source1_entity_id",
    "matched_entity_ids",
]


def parse_match_list(value: str) -> list[str]:
    """
    Convert the comma-separated matched_entity_ids field
    into a clean list.

    Empty value -> []
    """
    if value is None:
        return []

    value = str(value).strip()

    if not value:
        return []

    values = [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(values))


def validate_match_ids(match_ids: list[str]) -> None:
    """
    Every ground-truth match must be an S2 or S3 entity.
    """
    for entity_id in match_ids:
        if not (
            entity_id.startswith("S2-")
            or entity_id.startswith("S3-")
        ):
            raise ValueError(
                f"Invalid matched entity ID: {entity_id}"
            )


def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """
    Parse one ground-truth chunk and create match_count.
    """
    actual_columns = list(chunk.columns)

    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected columns.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Found: {actual_columns}"
        )

    source1_ids = (
        chunk["source1_entity_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    matched_values = (
        chunk["matched_entity_ids"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    parsed_match_lists = []

    for source1_id, matched_value in zip(
        source1_ids,
        matched_values,
    ):
        if not source1_id.startswith("S1-"):
            raise ValueError(
                f"Invalid Source 1 entity ID: {source1_id}"
            )

        match_ids = parse_match_list(matched_value)

        validate_match_ids(match_ids)

        parsed_match_lists.append(match_ids)

    output = pd.DataFrame(
        {
            "source1_entity_id": source1_ids,
            "matched_entity_ids": [
                ",".join(match_ids)
                for match_ids in parsed_match_lists
            ],
            "match_count": [
                len(match_ids)
                for match_ids in parsed_match_lists
            ],
        }
    )

    return output


def build_ground_truth() -> None:
    """
    Parse the complete ground-truth TSV in chunks.
    """
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

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

    for chunk_number, chunk in enumerate(
        reader,
        start=1,
    ):
        processed = process_chunk(chunk)

        processed.to_csv(
            OUTPUT_FILE,
            sep="\t",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            encoding="utf-8",
        )

        first_chunk = False
        total_rows += len(processed)

        print(
            f"Chunk {chunk_number:,} "
            f"| rows processed: {total_rows:,}"
        )

    print("\n" + "=" * 70)
    print("GROUND-TRUTH PARSING COMPLETE")
    print("=" * 70)
    print(f"Rows processed : {total_rows:,}")
    print(f"Output file    : {OUTPUT_FILE}")


def inspect_first_rows() -> None:
    """
    Read a few rows and demonstrate the parser.
    """
    print("GROUND-TRUTH PARSER TEST")
    print("=" * 70)

    sample = pd.read_csv(
        INPUT_FILE,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        nrows=5,
    )

    processed = process_chunk(sample)

    print(processed.to_string(index=False))


if __name__ == "__main__":
    build_ground_truth()