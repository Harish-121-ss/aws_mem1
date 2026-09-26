from pathlib import Path
from typing import Iterator

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_DIR = PROJECT_ROOT / "dataset" / "train"


SOURCE_COLUMNS = [
    "entity_id",
    "business_name",
    "business_address",
    "country",
]

GROUND_TRUTH_COLUMNS = [
    "source1_entity_id",
    "matched_entity_ids",
]


def get_train_file(filename: str) -> Path:
    """
    Return the full path to a training TSV file.
    """
    path = TRAIN_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Training file not found: {path}")

    return path


def load_source_in_chunks(
    filename: str,
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Read a source TSV file in chunks.

    This avoids loading the complete large dataset into memory.
    """
    path = get_train_file(filename)

    reader = pd.read_csv(
        path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        chunksize=chunk_size,
    )

    first_chunk = True

    for chunk in reader:
        if first_chunk:
            validate_columns(chunk, SOURCE_COLUMNS, filename)
            first_chunk = False

        yield chunk


def load_ground_truth_in_chunks(
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Read train_ground_truth.tsv in chunks.
    """
    filename = "train_ground_truth.tsv"
    path = get_train_file(filename)

    reader = pd.read_csv(
        path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        chunksize=chunk_size,
    )

    first_chunk = True

    for chunk in reader:
        if first_chunk:
            validate_columns(chunk, GROUND_TRUTH_COLUMNS, filename)
            first_chunk = False

        yield chunk


def validate_columns(
    dataframe: pd.DataFrame,
    expected_columns: list[str],
    filename: str,
) -> None:
    """
    Validate that the expected columns exist.
    """
    actual_columns = list(dataframe.columns)

    if actual_columns != expected_columns:
        raise ValueError(
            f"Unexpected columns in {filename}.\n"
            f"Expected: {expected_columns}\n"
            f"Found:    {actual_columns}"
        )


def get_source1_chunks(
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Iterate through Source 1 training records.
    """
    return load_source_in_chunks(
        "train_source1.tsv",
        chunk_size=chunk_size,
    )


def get_source2_chunks(
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Iterate through Source 2 training records.
    """
    return load_source_in_chunks(
        "train_source2.tsv",
        chunk_size=chunk_size,
    )


def get_source3_chunks(
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Iterate through Source 3 training records.
    """
    return load_source_in_chunks(
        "train_source3.tsv",
        chunk_size=chunk_size,
    )


def get_ground_truth_chunks(
    chunk_size: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """
    Iterate through ground-truth records.
    """
    return load_ground_truth_in_chunks(
        chunk_size=chunk_size,
    )


if __name__ == "__main__":
    print("Testing Member 1 data loader...\n")

    source_files = [
        ("Source 1", get_source1_chunks()),
        ("Source 2", get_source2_chunks()),
        ("Source 3", get_source3_chunks()),
    ]

    for source_name, chunks in source_files:
        first_chunk = next(chunks)

        print(f"{source_name}")
        print(f"  Rows in first chunk : {len(first_chunk):,}")
        print(f"  Columns             : {list(first_chunk.columns)}")
        print(
            f"  First entity_id     : "
            f"{first_chunk.iloc[0]['entity_id']}"
        )
        print()

    ground_truth = next(get_ground_truth_chunks())

    print("Ground Truth")
    print(f"  Rows in first chunk : {len(ground_truth):,}")
    print(f"  Columns             : {list(ground_truth.columns)}")
    print(
        f"  First source1 ID    : "
        f"{ground_truth.iloc[0]['source1_entity_id']}"
    )

    print("\nData loader test completed successfully.")