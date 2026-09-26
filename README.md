# Business Entity Resolution — Member 1

## Responsibility

Member 1 owns the data and normalization foundation for the Business Entity Resolution challenge.

## Implemented Components

### Data Processing

* TSV dataset inspection
* Chunked data loading
* Raw dataset validation
* Ground-truth parsing

### Normalization

* Business-name normalization
* Unicode-aware multilingual name handling
* Business-address normalization
* Address token extraction
* Address-number extraction
* Postal/PIN extraction
* Open-set country normalization

### Validation

* Entity-level train/validation split
* Reproducible split using random seed 42
* 90% training / 10% validation split

### Pair Preparation

* Ground-truth positive-pair generation
* Candidate-pair labeling utility for true/false matching labels

## Repository Structure

```text
src/
├── data/
│   ├── ground_truth.py
│   ├── inspect_dataset.py
│   ├── label_candidate_pairs.py
│   ├── loader.py
│   ├── pair_builder.py
│   └── validate_dataset.py
│
├── normalization/
│   ├── add_address_features.py
│   ├── add_address_features_all.py
│   ├── add_country_features.py
│   ├── address_normalizer.py
│   ├── country_normalizer.py
│   ├── name_normalizer.py
│   └── normalize_names.py
│
└── validation/
    └── create_split.py
```

## Generated Local Artifacts

The following are generated locally and intentionally excluded from Git:

```text
dataset/
data/
```

They contain the challenge datasets and generated normalized/pair artifacts.

## Validation Split

The current validation split contains:

* Total Source 1 entities: 2,206,821
* Training entities: 1,986,139
* Validation entities: 220,682
* Random seed: 42
* Validation ratio: 0.10
* Train/validation overlap: 0

## Handoff

Member 1 provides:

* normalized source records
* parsed ground truth
* validation split
* positive-pair artifact
* candidate-pair labeling utility

These artifacts are intended for the later blocking and pairwise matching stages.
