from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

POSITIVE_PAIRS_FILE = (
    PROJECT_ROOT
    / "data"
    / "pairs"
    / "positive_pairs.tsv"
)


def label_candidate_pair(
    source1_entity_id: str,
    candidate_entity_id: str,
    ground_truth: dict[str, set[str]],
) -> int:
    """
    Return:
        1 -> true match
        0 -> non-match
    """
    matched_ids = ground_truth.get(
        source1_entity_id,
        set(),
    )

    return int(
        candidate_entity_id in matched_ids
    )


def label_candidate_dataframe(
    candidate_df: pd.DataFrame,
    ground_truth: dict[str, set[str]],
) -> pd.DataFrame:
    """
    Add a binary label column to candidate pairs.

    Required columns:
        source1_entity_id
        candidate_entity_id
    """
    required_columns = {
        "source1_entity_id",
        "candidate_entity_id",
    }

    missing = required_columns.difference(
        candidate_df.columns
    )

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    result = candidate_df.copy()

    result["label"] = [
        label_candidate_pair(
            source1_entity_id,
            candidate_entity_id,
            ground_truth,
        )
        for source1_entity_id, candidate_entity_id
        in zip(
            result["source1_entity_id"],
            result["candidate_entity_id"],
        )
    ]

    return result


def self_test() -> None:
    """
    Fast self-test.

    Only reads 10 positive pairs. It does NOT load the
    complete 2.2M-row ground-truth file.
    """
    sample = pd.read_csv(
        POSITIVE_PAIRS_FILE,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        nrows=10,
    )

    ground_truth = {}

    for _, row in sample.iterrows():
        source1_id = row["source1_entity_id"]
        candidate_id = row["candidate_entity_id"]

        ground_truth.setdefault(
            source1_id,
            set(),
        ).add(candidate_id)

    labeled = label_candidate_dataframe(
        sample[
            [
                "source1_entity_id",
                "candidate_entity_id",
            ]
        ],
        ground_truth,
    )

    print("CANDIDATE PAIR LABELER TEST")
    print("=" * 70)
    print(labeled.to_string(index=False))

    if not (labeled["label"] == 1).all():
        raise RuntimeError(
            "Self-test failed."
        )

    print()
    print("Self-test passed.")


if __name__ == "__main__":
    self_test()