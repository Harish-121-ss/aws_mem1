"""Small Member 3 integration example for disk-backed record lookup."""
from src.data.disk_lookup import DiskEntityLookup
INDEX="data/lookup/entity_lookup.sqlite3"
candidate_ids=["S2-681193310","S3-775321672","S2-743505751"]
with DiskEntityLookup(INDEX) as lookup:
    records=lookup.get_many(candidate_ids)
for candidate_id,record in zip(candidate_ids,records):
    if record is None: print(candidate_id,"NOT FOUND")
    else: print(candidate_id,record["business_name_normalized"],record["country_normalized"])
