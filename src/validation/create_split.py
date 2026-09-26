from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

GROUND_TRUTH_FILE = (
    PROJECT_ROOT
    / "data"
    / "ground_truth"
    / "ground_truth_parsed.tsv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "validation"

OUTPUT_FILE = OUTPUT_DIR / "validation_split.json"

RANDOM_SEED = 42
VALIDATION_RATIO = 0.10


def create_validation_split() -> None:
    print("MEMBER 1 - VALIDATION SPLIT")
    print("=" * 70)

    if not GROUND_TRUTH_FILE.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: {GROUND_TRUTH_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Reading Source 1 entity IDs...")

    df = pd.read_csv(
        GROUND_TRUTH_FILE,
        sep="\t",
        dtype={
            "source1_entity_id": "string",
            "matched_entity_ids": "string",
            "match_count": "int32",
        },
        keep_default_na=False,
        usecols=[
            "source1_entity_id",
            "match_count",
        ],
    )

    # Remove accidental duplicate IDs defensively.
    df = df.drop_duplicates(
        subset=["source1_entity_id"]
    ).reset_index(drop=True)

    entity_ids = df["source1_entity_id"].to_numpy()

    rng = np.random.default_rng(RANDOM_SEED)

    shuffled_indices = rng.permutation(
        len(entity_ids)
    )

    validation_size = int(
        len(entity_ids) * VALIDATION_RATIO
    )

    validation_indices = shuffled_indices[
        :validation_size
    ]

    train_indices = shuffled_indices[
        validation_size:
    ]

    train_ids = entity_ids[train_indices]
    validation_ids = entity_ids[validation_indices]

    train_set = set(train_ids)
    validation_set = set(validation_ids)

    # Safety checks.
    overlap = train_set.intersection(
        validation_set
    )

    if overlap:
        raise RuntimeError(
            f"Train/validation overlap detected: "
            f"{len(overlap)} entities"
        )

    if (
        len(train_set) + len(validation_set)
        != len(entity_ids)
    ):
        raise RuntimeError(
            "Train + validation entities do not "
            "cover all Source 1 entities."
        )

    result = {
        "random_seed": RANDOM_SEED,
        "validation_ratio": VALIDATION_RATIO,
        "total_entities": int(len(entity_ids)),
        "training_entities": int(len(train_ids)),
        "validation_entities": int(len(validation_ids)),
        "train_source1_entity_ids": sorted(
            train_ids.tolist()
        ),
        "validation_source1_entity_ids": sorted(
            validation_ids.tolist()
        ),
    }

    import json

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    print()
    print(f"Total Source 1 entities : {len(entity_ids):,}")
    print(f"Training entities       : {len(train_ids):,}")
    print(f"Validation entities     : {len(validation_ids):,}")
    print(f"Overlap                 : {len(overlap):,}")

    print()
    print(f"Saved to:")
    print(OUTPUT_FILE)

    print()
    print("VALIDATION SPLIT COMPLETE")


if __name__ == "__main__":
    create_validation_split()