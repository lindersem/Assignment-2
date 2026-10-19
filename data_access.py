"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""

import json
import csv
import os
import data_access
from datetime import datetime


# task 1
def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


def generalised_load_json(path):
    skipped_file = 0
    contents = []
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            full_path = os.path.join(path, filename)
            try:
                with open(full_path, "r") as file:
                    content = json.load(file)
                    contents.append(content)
            except (json.JSONDecodeError, FileNotFoundError):
                skipped_file += 1
                print(f"Invalid json file {filename}")
    return contents, skipped_file


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
    required_keys = ["vessel_id", "name", "imo", "capacity_teu"]
    contents, skipped_file = generalised_load_json(directory)
    for vessel in contents:
        if all(key in vessel for key in required_keys):
            valid_vessels.append(vessel)
        else:
            skipped_file += 1
            print("Missing required field")

    valid_vessels.sort(key=lambda vessel: vessel["name"].lower())
    return valid_vessels, skipped_file


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


def get_vessel_by_name(name):
    vessel = data_access.find_json_record("dataset/vessels", "name", name)
    if vessel:
        return vessel
    return None


def is_valid_date(date_string):  # YYYY-MM-DD
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# task 8
def validate_vessel_input():
    vessel_input = input("Vessel name: ").strip().lower()
    vessel = find_json_record("dataset/vessels", "name", vessel_input)
    # validate vessel name input
    if not vessel:
        print("Vessel not found")
        return None, None, False
    else:
        official_vessel_name = vessel["name"]
        vessel_id = vessel["vessel_id"]
        valid_vessel_input = True
    return official_vessel_name, vessel_id, valid_vessel_input


def validate_date_input():
    date_is_valid = False
    while not date_is_valid:
        reference_date = input("Reference date: ").strip()
        if is_valid_date(reference_date):
            date_is_valid = True
            return reference_date
        else:
            print("Error - Date must use YYYY-MM-DD")
            date_is_valid = False


# task 9
def is_cache_outdated(cache_path, source_dir):
    # get the modification time of the cache file, if it exists
    cache_time = os.path.getmtime(cache_path)
    # check every file in the incident directory
    for filename in os.listdir(source_dir):
        if filename.endswith(".json"):
            full_path = os.path.join(source_dir, filename)
            # if file is newer -> cache is outdated
            if os.path.getmtime(full_path) > cache_time:
                return True
    return False


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        # indent=4 makes the JSON readable
        json.dump(data, file, indent=4)
