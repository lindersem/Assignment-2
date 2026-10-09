"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
import json
import os


def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)
    

def load_vessels(directory):
    valid_vessels = []
    skipped_vessel_file = 0
    required_keys = ["vessel_id", "name", "imo", "capacity_teu"]
    for vessels_filename in os.listdir(directory):
        #get path by directory + filename
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
            skipped_vessel_file +=1
            print(f"Invalid JSON file: {vessels_filename}")
    valid_vessels.sort(key=lambda vessel: vessel["name"].lower())
    return valid_vessels, skipped_vessel_file
            
