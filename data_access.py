"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""

import json
import csv
import os


# task 1
def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


# task 2
def load_csv(path):
    with open(path, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)


# task 4
def load_every_json(path):
    all_json = []
    for incident_filename in os.listdir(path):
        full_path = os.path.join(path, incident_filename)
        all_json.append(load_json(full_path))
        return all_json


# task 1
def load_vessels(directory):
    valid_vessels = []
    skipped_vessel_file = 0
    required_keys = ["vessel_id", "name", "imo", "capacity_teu"]
    for vessels_filename in os.listdir(directory):
        # get path by directory + filename
        path = os.path.join(directory, vessels_filename)
        try:
            vessel = load_json(path)
            valid = True
            for i in required_keys:
                if i not in vessel:
                    valid = False
                    break

            if valid:
                valid_vessels.append(vessel)
            else:
                skipped_vessel_file += 1
                print(f"Missing required field: {vessels_filename}")

        except json.JSONDecodeError:
            skipped_vessel_file += 1
            print(f"Invalid JSON file: {vessels_filename}")
    valid_vessels.sort(key=lambda vessel: vessel["name"].lower())
    return valid_vessels, skipped_vessel_file


# task 2
def find_csv_record(path, column, value):
    data = load_csv(path)
    for row in data:
        if row.get(column) and str(row.get(column)).lower() == str(value).lower():
            return row
    return None


# task 2
def find_json_record(directory, key, value):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            full_path = os.path.join(directory, filename)
            try:
                record = load_json(full_path)
                if (
                    record
                    and record.get(key)
                    and str(record.get(key)).lower() == str(value).lower()
                ):
                    return record
            except json.JSONDecodeError:
                continue
    return None


# task 2
def list_registered_vessels(directory):
    valid_vessels = []
    required_keys = ["vessel_id", "name", "imo", "capacity_teu"]

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        try:
            vessel = load_json(path)
            if all(key in vessel for key in required_keys):
                valid_vessels.append(vessel)
        except (json.JSONDecodeError, FileNotFoundError):
            continue

    valid_vessels.sort(key=lambda v: v["name"].lower())
    return valid_vessels
