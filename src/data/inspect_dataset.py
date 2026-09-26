from pathlib import Path
import csv


TRAIN_DIR = Path("dataset/train")

FILES = {
    "Source 1": TRAIN_DIR / "train_source1.tsv",
    "Source 2": TRAIN_DIR / "train_source2.tsv",
    "Source 3": TRAIN_DIR / "train_source3.tsv",
    "Ground Truth": TRAIN_DIR / "train_ground_truth.tsv",
}


def inspect_file(label: str, path: Path, sample_size: int = 3) -> None:
    print("\n" + "=" * 70)
    print(f"{label}: {path}")
    print("=" * 70)

    if not path.exists():
        print("ERROR: File does not exist.")
        return

    print(f"File size: {path.stat().st_size / (1024 * 1024):,.2f} MB")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter="\t")

        header = next(reader)
        print(f"Columns: {header}")

        print("\nSample rows:")
        for i, row in enumerate(reader):
            print(row)
            if i + 1 >= sample_size:
                break


def main() -> None:
    print("BUSINESS ENTITY RESOLUTION - DATASET INSPECTION")
    print(f"Training directory: {TRAIN_DIR.resolve()}")

    for label, path in FILES.items():
        inspect_file(label, path)

    print("\nInspection complete.")


if __name__ == "__main__":
    main()