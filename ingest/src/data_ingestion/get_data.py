# ingest_files.py

import os
import json
from tqdm import tqdm

import constants
from data_ingestion.ingest_files import list_all_files
from data_ingestion.utils.get_class_list import extract_defs
from data_ingestion.git_meta import get_file_meta

# Load already-processed paths
if os.path.exists(constants.PROGRESS_FILE):
    with open(constants.PROGRESS_FILE, "r") as f:
        processed = set(json.load(f))
else:
    processed = set()

# Gather all files up front to get a total count
all_paths = list(list_all_files(constants.repo_path))
total_files = len(all_paths)

# Open checkpoint for append
out_f = open(constants.CHECKPOINT_FILE, "a", encoding="utf-8")

def something():

    try:
        # Wrap in tqdm for a progress bar
        for path in tqdm(all_paths, desc="Ingesting files", unit="file"):
            if path in processed:
                continue

            # Build record
            with open(path, encoding="utf-8") as f:
                text = f.read()
            record = {
                "path":        path,
                "text":        text,
                "definitions": extract_defs(text) if path.endswith(".py") else [],
                "git":         get_file_meta(path)
            }

            # Write & flush
            out_f.write(json.dumps(record) + "\n")
            out_f.flush()

            # Mark progress
            processed.add(path)
            with open(constants.PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump(list(processed), pf)

    finally:
        out_f.close()
