from pathlib import Path
import pytest
from src.data.build_lookup_index import build_lookup_index
from src.data.disk_lookup import DiskEntityLookup, LookupIntegrityError, SOURCE_COLUMNS

def write_tsv(path: Path, rows, newline="\n"):
    with path.open("wb") as fh:
        fh.write(("\t".join(SOURCE_COLUMNS)+newline).encode("utf-8"))
        for row in rows: fh.write(("\t".join(row)+newline).encode("utf-8"))

def row(entity, name="name", country="us"):
    return [entity,name,"",country,name,'["name"]',"","[]","[]","",country]

def make_data(tmp_path, newline="\n"):
    data=tmp_path/"normalized"; data.mkdir()
    write_tsv(data/"normalized_source1.tsv",[row("S1-1","alpha"),row("S1-2","")],newline)
    write_tsv(data/"normalized_source2.tsv",[row("S2-1","beta")],newline)
    write_tsv(data/"normalized_source3.tsv",[row("S3-1","gamma")],newline)
    return data

def test_build_and_ordered_lookup(tmp_path):
    data=make_data(tmp_path); index=tmp_path/"lookup.sqlite3"; build_lookup_index(data,index)
    with DiskEntityLookup(index) as lookup:
        assert lookup.get("S1-1")["business_name"]=="alpha"
        records=lookup.get_many(["S3-1","missing","S1-2","S2-1"])
        assert [r["entity_id"] if r else None for r in records]==["S3-1",None,"S1-2","S2-1"]
        assert records[2]["business_name"]==""

def test_crlf_is_safe(tmp_path):
    data=make_data(tmp_path,"\r\n"); index=tmp_path/"lookup.sqlite3"; build_lookup_index(data,index)
    with DiskEntityLookup(index) as lookup: assert lookup.get("S2-1")["entity_id"]=="S2-1"

def test_duplicate_ids_rejected(tmp_path):
    data=tmp_path/"normalized"; data.mkdir()
    write_tsv(data/"normalized_source1.tsv",[row("S1-1"),row("S1-1")])
    write_tsv(data/"normalized_source2.tsv",[row("S2-1")]); write_tsv(data/"normalized_source3.tsv",[row("S3-1")])
    with pytest.raises(ValueError,match="Duplicate entity_id"): build_lookup_index(data,tmp_path/"lookup.sqlite3")

def test_changed_file_rejected(tmp_path):
    data=make_data(tmp_path); index=tmp_path/"lookup.sqlite3"; build_lookup_index(data,index)
    with (data/"normalized_source1.tsv").open("ab") as fh: fh.write(b" ")
    with pytest.raises(LookupIntegrityError,match="changed"): DiskEntityLookup(index)

def test_strict_hash_verification(tmp_path):
    data=make_data(tmp_path); index=tmp_path/"lookup.sqlite3"; build_lookup_index(data,index)
    path=data/"normalized_source1.tsv"; path.write_bytes(path.read_bytes().replace(b"alpha",b"alphA"))
    with pytest.raises(LookupIntegrityError): DiskEntityLookup(index,verify_hash=True)
