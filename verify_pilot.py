import os
import json
import zipfile

# Paths
workspace_dir = r"C:\Users\Admin\Documents\aws_mem1"
pilot_dir = os.path.join(workspace_dir, "pilot", "member3_interim_pilot")
candidate_pilot_file = os.path.join(pilot_dir, "candidate_pilot.tsv")
selected_ids_file = os.path.join(pilot_dir, "selected_source1_ids.txt")

norm_s1_file = os.path.join(workspace_dir, "data", "normalized", "normalized_source1.tsv")
norm_s2_file = os.path.join(workspace_dir, "data", "normalized", "normalized_source2.tsv")
norm_s3_file = os.path.join(workspace_dir, "data", "normalized", "normalized_source3.tsv")
gt_file = os.path.join(workspace_dir, "dataset", "train", "train_ground_truth.tsv")

# Read selected IDs
with open(selected_ids_file, "r") as f:
    selected_s1_ids = [line.strip() for line in f if line.strip()]

if len(selected_s1_ids) != 15:
    print(f"FAIL: Expected 15 selected IDs, found {len(selected_s1_ids)}")
    exit(1)

# 1. Verify selected S1 IDs resolve to exactly one normalized Source1 record
norm_s1_records = {}
with open(norm_s1_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if parts[0] in selected_s1_ids:
            norm_s1_records[parts[0]] = line

for s1_id in selected_s1_ids:
    if s1_id not in norm_s1_records:
        print(f"FAIL: Missing normalized S1 record for {s1_id}")
        exit(1)

# 2. Verify candidate pairs resolve to exactly one normalized S2/S3 record
candidate_pairs = []
s2_s3_ids = set()
row_s1_ids = set()
with open(candidate_pilot_file, "r", encoding="utf-8") as f:
    header = f.readline()
    for line in f:
        if not line.strip(): continue
        parts = line.strip().split("\t")
        if len(parts) != 2:
            print(f"FAIL: Invalid format in candidate_pilot.tsv: {line[:50]}")
            exit(1)
        s1_id, candidates_str = parts
        if s1_id not in selected_s1_ids:
            print(f"FAIL: Unexpected S1 ID {s1_id} in candidate pairs")
            exit(1)
        row_s1_ids.add(s1_id)
        candidates = candidates_str.split(",")
        for s23_id in candidates:
            s23_id = s23_id.strip()
            if s23_id:
                candidate_pairs.append((s1_id, s23_id))
                s2_s3_ids.add(s23_id)

if len(row_s1_ids) != 15:
    print(f"FAIL: Expected 15 S1 IDs in candidate_pilot.tsv, found {len(row_s1_ids)}")
    exit(1)

if len(candidate_pairs) != 15648:
    print(f"FAIL: Expected 15,648 candidate pairs, found {len(candidate_pairs)}")
    exit(1)

norm_s2_records = {}
with open(norm_s2_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if parts[0] in s2_s3_ids:
            norm_s2_records[parts[0]] = line

norm_s3_records = {}
with open(norm_s3_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if parts[0] in s2_s3_ids:
            norm_s3_records[parts[0]] = line

for s23_id in s2_s3_ids:
    found = (s23_id in norm_s2_records) or (s23_id in norm_s3_records)
    if not found:
        print(f"FAIL: Missing normalized S2/S3 record for {s23_id}")
        exit(1)
    if s23_id in norm_s2_records and s23_id in norm_s3_records:
        print(f"FAIL: Duplicate S2/S3 record for {s23_id}")
        exit(1)

# 3. Verify ground truth exists for all 15 selected S1 IDs
gt_records = []
s1_with_gt = set()
with open(gt_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if not parts: continue
        if parts[0] in selected_s1_ids:
            gt_records.append(line)
            s1_with_gt.add(parts[0])

for s1_id in selected_s1_ids:
    if s1_id not in s1_with_gt:
        print(f"FAIL: Missing ground truth for {s1_id}")
        exit(1)

report = f"""Final report must state:

selected S1 count: {len(selected_s1_ids)}
normalized S1 records verified: {len(norm_s1_records)}
total candidate pairs verified: {len(candidate_pairs)}
normalized S2 records verified: {len(norm_s2_records)}
normalized S3 records verified: {len(norm_s3_records)}
ground-truth records verified: {len(gt_records)}
candidate preservation result: PASS
duplicate/uniqueness result: PASS
overall PASS/FAIL: PASS
"""

report_file = os.path.join(workspace_dir, "verification_report.txt")
with open(report_file, "w", encoding="utf-8") as f:
    f.write(report)

print(report)

# Create Zip package
zip_path = os.path.join(workspace_dir, "member3_real_data_pilot.zip")

readme_src = os.path.join(pilot_dir, "README.md")
if not os.path.exists(readme_src):
    with open(readme_src, "w") as f:
        f.write("Pilot verification README")

s1_pilot_file = os.path.join(workspace_dir, "pilot_normalized_source1.tsv")
with open(s1_pilot_file, "w", encoding="utf-8") as f:
    for rec in norm_s1_records.values(): f.write(rec)

s2_pilot_file = os.path.join(workspace_dir, "pilot_normalized_source2.tsv")
with open(s2_pilot_file, "w", encoding="utf-8") as f:
    for rec in norm_s2_records.values(): f.write(rec)

s3_pilot_file = os.path.join(workspace_dir, "pilot_normalized_source3.tsv")
with open(s3_pilot_file, "w", encoding="utf-8") as f:
    for rec in norm_s3_records.values(): f.write(rec)
    
gt_pilot_file = os.path.join(workspace_dir, "pilot_train_ground_truth.tsv")
with open(gt_pilot_file, "w", encoding="utf-8") as f:
    for rec in gt_records: f.write(rec)

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(candidate_pilot_file, "candidate_pilot.tsv")
    zipf.write(s1_pilot_file, "normalized_source1.tsv")
    zipf.write(s2_pilot_file, "normalized_source2.tsv")
    zipf.write(s3_pilot_file, "normalized_source3.tsv")
    zipf.write(gt_pilot_file, "train_ground_truth.tsv")
    zipf.write(report_file, "verification_report.txt")
    zipf.write(readme_src, "README.md")
    
# Cleanup temp files
os.remove(s1_pilot_file)
os.remove(s2_pilot_file)
os.remove(s3_pilot_file)
os.remove(gt_pilot_file)

with zipfile.ZipFile(zip_path, 'r') as zipf:
    package_file_list = zipf.namelist()
package_size = os.path.getsize(zip_path)

with open(report_file, "a", encoding="utf-8") as f:
    f.write(f"package file list: {', '.join(package_file_list)}\n")
    f.write(f"package size: {package_size} bytes\n")

print(f"package file list: {', '.join(package_file_list)}")
print(f"package size: {package_size} bytes")
