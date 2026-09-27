# Disk-backed normalized-record lookup

Member 1's minimal disk-backed layer preserves the existing normalized TSV contract and adds a read-only SQLite byte-offset index. Challenge datasets and generated indexes stay local and are ignored by the existing `/data/` and `/dataset/` rules.

## Build
```cmd
python src\data\build_lookup_index.py --data-dir data\normalized --index data\lookup\entity_lookup.sqlite3
```
Inputs: `data/normalized/normalized_source1.tsv`, `normalized_source2.tsv`, `normalized_source3.tsv`.

The builder scans each file in binary mode, records the byte offset for each entity_id, computes SHA-256 during that scan, rejects duplicate IDs/schema/UTF-8/field-count errors, and verifies the source did not change while indexing. It supports LF and Windows CRLF.

## API
```python
from src.data.disk_lookup import DiskEntityLookup
with DiskEntityLookup("data/lookup/entity_lookup.sqlite3") as lookup:
    record=lookup.get("S1-965667")
    records=lookup.get_many(["S2-681193310","S3-775321672"])
```
`get()` returns a normalized record dict or None. `get_many()` preserves input order and returns None for absent IDs. Empty-string missing values are preserved. No normalization is performed here.

## Member 3 integration
Replace the current in-memory catalog with one `DiskEntityLookup` instance. For each bounded candidate batch, call `get_many(batch_candidate_entity_ids)` and zip results back to the original candidate IDs. Returned fields are the existing normalized 11-column schema:
`entity_id`, `business_name`, `business_address`, `country`, `business_name_normalized`, `business_name_tokens`, `business_address_normalized`, `address_tokens`, `address_numbers`, `postal_codes`, `country_normalized`.

Validation remains unchanged at `data/validation/validation_split.json`; this layer does not alter it.

Normal startup checks source size and nanosecond mtime. For strict content verification after copying files, use `DiskEntityLookup(index, verify_hash=True)`.

Do not commit normalized TSVs, SQLite indexes, or other challenge-data artifacts.
