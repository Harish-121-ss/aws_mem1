from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

GROUND_TRUTH_FILE = (
    PROJECT_ROOT
    / "data"
    / "ground_truth"
    / "ground_truth_parsed.tsv"
)

VALIDATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "validation_split.json"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "pairs"

POSITIVE_PAIRS_FILE = (
    OUTPUT_DIR
    / "positive_pairs.tsv"
)

CHUNK_SIZE = 100_000


def load_validation_ids() -> set[str]:
    """
    Load Source 1 validation IDs so every positive pair
    can be assigned to train or validation.
    """
    with VALIDATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return set(
        data["validation_source1_entity_ids"]
    )


def get_candidate_source(entity_id: str) -> str:
    """
    Identify whether a matched entity comes from Source 2 or 3.
    """
    if entity_id.startswith("S2-"):
        return "source2"

    if entity_id.startswith("S3-"):
        return "source3"

    raise ValueError(
        f"Invalid matched entity ID: {entity_id}"
    )


def build_positive_pairs() -> None:
    print("MEMBER 1 - POSITIVE PAIR BUILDER")
    print("=" * 70)

    if not GROUND_TRUTH_FILE.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: "
            f"{GROUND_TRUTH_FILE}"
        )

    if not VALIDATION_FILE.exists():
        raise FileNotFoundError(
            f"Validation split not found: "
            f"{VALIDATION_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if POSITIVE_PAIRS_FILE.exists():
        POSITIVE_PAIRS_FILE.unlink()

    validation_ids = load_validation_ids()

    print(
        f"Validation entities loaded: "
        f"{len(validation_ids):,}"
    )

    reader = pd.read_csv(
        GROUND_TRUTH_FILE,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
        chunksize=CHUNK_SIZE,
    )

    first_chunk = True

    total_source1_rows = 0
    total_positive_pairs = 0
    train_pairs = 0
    validation_pairs = 0

    for chunk_number, chunk in enumerate(
        reader,
        start=1,
    ):
        rows = []

        for _, row in chunk.iterrows():

            source1_id = row["source1_entity_id"]
            matched_ids_text = row["matched_entity_ids"]

            if not matched_ids_text:
                continue

            split_name = (
                "validation"
                if source1_id in validation_ids
                else "train"
            )

            matched_ids = [
                value.strip()
                for value in matched_ids_text.split(",")
                if value.strip()
            ]

            for matched_id in matched_ids:
                rows.append(
                    {
                        "source1_entity_id": source1_id,
                        "candidate_entity_id": matched_id,
                        "candidate_source": get_candidate_source(
                            matched_id
                        ),
                        "label": 1,
                        "split": split_name,
                    }
                )

                total_positive_pairs += 1

                if split_name == "train":
                    train_pairs += 1
                else:
                    validation_pairs += 1

        if rows:
            output_chunk = pd.DataFrame(rows)

            output_chunk.to_csv(
                POSITIVE_PAIRS_FILE,
                sep="\t",
                index=False,
                mode="w" if first_chunk else "a",
                header=first_chunk,
                encoding="utf-8",
            )

            first_chunk = False

        total_source1_rows += len(chunk)

        print(
            f"Chunk {chunk_number:,} "
            f"| S1 rows: {total_source1_rows:,} "
            f"| positive pairs: {total_positive_pairs:,}"
        )

    print()
    print("=" * 70)
    print("POSITIVE PAIR BUILD COMPLETE")
    print("=" * 70)
    print(
        f"Positive pairs      : "
        f"{total_positive_pairs:,}"
    )
    print(
        f"Training pairs      : "
        f"{train_pairs:,}"
    )
    print(
        f"Validation pairs    : "
        f"{validation_pairs:,}"
    )
    print(
        f"Output              : "
        f"{POSITIVE_PAIRS_FILE}"
    )


if __name__ == "__main__":
    build_positive_pairs()