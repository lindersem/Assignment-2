"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import json
import csv
import os
import data_access
from datetime import datetime


# task 2 (Avery: Move to dataaccess?)
def get_vessel_by_name(name):
    vessel = data_access.find_json_record("dataset/vessels", "name", name)
    if vessel:
        return vessel
    return None


# task 2 (Avery: Move to dataaccess?)
def is_valid_date(date_string):  # YYYY-MM-DD
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# task 2
def find_earliest_call(vessel_id, reference_date):  # date on or after
    all_calls = data_access.load_csv("dataset/port_calls.csv")

    filtered_calls = []
    for call in all_calls:
        if (
            call.get("vessel_id") == vessel_id
            and call.get("arrival_date")
            and call.get("arrival_date") >= reference_date
        ):  # ISO dates (YYYY-MM-DD) compare as strings
            filtered_calls.append(call)

    if not filtered_calls:
        return None
    filtered_calls.sort(key=lambda x: (x["arrival_date"], x["call_id"]))
    return filtered_calls[0]


# task 2
def resolve_manifest(call_id):
    manifest_path = f"dataset/manifests/{call_id.lower()}.json"
    try:
        manifest = data_access.load_json(manifest_path)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if not manifest:
        return None
    resolved_shipments = []
    total_weight = 0.0
    missing_count = 0
    shipment_ids = manifest.get("shipment_ids", [])
    for shipment_id in shipment_ids:
        shipment = data_access.find_json_record(
            "dataset/shipments", "shipment_id", shipment_id
        )
        if shipment:
            resolved_shipments.append(shipment)
            total_weight += float(shipment.get("weight_kg", 0))
        else:
            resolved_shipments.append({"shipment_id": shipment_id, "missing": True})
            missing_count += 1
    return {
        "call_id": call_id,
        "shipments": resolved_shipments,
        "total_weight": total_weight,
        "missing_count": missing_count,
        "declared_count": len(shipment_ids),
    }


# task 3
def classify_shipment(shipment):
    """Classify a single shipment dictionary into a category and reason."""
    if shipment.get("hazardous", False):
        return "CONTROLLED", "hazardous cargo"
    elif shipment.get("temperature_controlled", False):
        return "COLD CHAIN", "temperature-controlled cargo"
    elif shipment.get("priority") == "EXPRESS" or shipment.get("weight_kg", 0) >= 5000:
        return "EXPEDITE", "express service"
    return "STANDARD", "standard cargo"


def process_priority_cargo(call_id_input):
    """Validate call, load manifest, classify shipments, and return results."""
    # Clean up user input (remove extra spaces and handle lowercase/uppercase)
    call_id_input = call_id_input.strip()

    # 1. Validate port call against port_calls.csv
    port_call = data_access.find_csv_record(
        "dataset/port_calls.csv", "call_id", call_id_input
    )
    if not port_call:
        return {"error": "Port call not found."}

    # 2. Try loading the manifest (using lowercase call_id to match file naming conventions)
    manifest_path = f"dataset/manifests/{port_call['call_id'].lower()}.json"
    try:
        manifest = data_access.load_json(manifest_path)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"error": "Manifest unavailable."}

    if not manifest or "shipment_ids" not in manifest:
        return {"error": "Manifest unavailable."}

    # 3. Resolve and classify shipments
    shipment_results = []
    category_counts = {"CONTROLLED": 0, "COLD CHAIN": 0, "EXPEDITE": 0, "STANDARD": 0}

    for shipment_id in manifest.get("shipment_ids", []):
        shipment = data_access.find_json_record(
            "dataset/shipments", "shipment_id", shipment_id
        )
        if shipment:
            category, reason = classify_shipment(shipment)
            shipment_results.append(
                {"shipment_id": shipment_id, "category": category, "reason": reason}
            )
            if category in category_counts:
                category_counts[category] += 1

    return {
        "call_id": port_call["call_id"],
        "shipments": shipment_results,
        "counts": category_counts,
    }


# Task 4
def export_customer_operations_profile(customer_input):
    customer_input = customer_input.strip().lower()

    # --- Part 2: Find all shipments for this customer, return list of dictionaries---
    matching_shipments = []
    shipments = data_access.load_every_json("dataset/shipments")
    for shipment in shipments:
        if shipment["customer"].strip().lower() == customer_input:
            matching_shipments.append(shipment)

    # --- Part 3: Validate if any were found ---
    if not matching_shipments:  # if list is empty
        print("Customer not found.")
        return

    # --- Part 4: Calculate profile statistics ---
    shipment_count = len(matching_shipments)
    total_weight_kg = 0.0
    express_count = 0
    destinations = []

    for shipment in matching_shipments:
        total_weight_kg += shipment["weight_kg"]
        if shipment["priority"] == "EXPRESS":
            express_count += 1
        destinations.append(shipment["destination"])

    # Clean destinations, remove duplicates and sort
    clean_destinations = "|".join(sorted(set(destinations)))
    first_shipment = matching_shipments[0]
    customer_name = first_shipment["customer"]
    customer_dictionary_output = {
        "customer": customer_name,
        "shipment_count": shipment_count,
        "total_weight_kg": f"{total_weight_kg:.2f}",
        "express_count": express_count,
        "destinations": clean_destinations,
    }

    # --- Part 5: Write exports, if customer exists update or append to customer-profiles.csv ---
    # Use an in-memory list to update the CSV safely:
    # Text files on disk cannot be edited in-place when row lengths change.
    # As required by the spec, we read existing rows into memory, replace
    # matching customer data (or keep other customers untouched), and rewrite safely.
    existing_rows = []
    customer_found = False
    csv_path = "exports/customer-profiles.csv"

    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["customer"].strip().lower() == customer_input:
                    existing_rows.append(customer_dictionary_output)
                    customer_found = True
                else:
                    existing_rows.append(row)

    # If brand new customer, append their row to the list
    if not customer_found:
        existing_rows.append(customer_dictionary_output)

    # Ensure exports directory exists and write back to CSV safely
    os.makedirs("exports", exist_ok=True)
    fieldnames = [
        "customer",
        "shipment_count",
        "total_weight_kg",
        "express_count",
        "destinations",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)

    print("Customer profile updated: exports/customer-profiles.csv")


# Task 5: Find port calls by month
def sort_by_date_and_vessel(call):  # gives .sort() the functions so it can sort
    return (call["arrival_date"], call["vessel_name"])


def find_port_calls_by_month(month):
    # --- PART 1: LOAD DATA ---
    all_calls = data_access.load_csv("dataset/port_calls.csv")
    matching_calls = []

    # --- PART 2: FILTER CALLS FOR THIS MONTH ---
    for call in all_calls:
        date_string = call["arrival_date"]
        vessel_id = call["vessel_id"]
        # Skip bad dates
        if not is_valid_date(date_string):
            continue

        # Look up the ship
        vessel = data_access.find_json_record("dataset/vessels", "vessel_id", vessel_id)
        if vessel is None:
            continue

        # Check if month matches
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
        if date_object.month == month:
            call["vessel_name"] = vessel["name"]
            matching_calls.append(call)

    # --- PART 3: CHECK IF EMPTY ---
    if len(matching_calls) == 0:
        print("No port calls found.")
        return None

    # --- PART 4: SORT by using function---
    matching_calls.sort(key=sort_by_date_and_vessel)

    # --- PART 5: PRINT RESULTS ---
    month_name = datetime(2026, month, 1).strftime("%B")
    print(f"Port calls in {month_name}:")
    for call in matching_calls:
        date_object = datetime.strptime(call["arrival_date"], "%Y-%m-%d")
        clean_date = date_object.strftime("%d %B %Y")
        ship_name = call["vessel_name"]
        port = call["port_code"]
        call_id = call["call_id"]
        print(f"- {clean_date} | {ship_name} | {port} | {call_id}")


# task 7
def get_longest_stable_sequence(event_codes):
    start = 0
    max_start = 0
    max_length = 0
    last_seen = {}

    for end, code in enumerate(event_codes):
        if code in last_seen and last_seen[code] >= start:
            start = last_seen[code] + 1

        last_seen[code] = end
        current_length = end - start + 1

        if current_length > max_length:
            max_length = current_length
            max_start = start

    longest_seq = event_codes[max_start : max_start + max_length]
    return longest_seq, max_length


def get_sequence_for_port_call(call_id):
    call_id = call_id.strip()

    port_call = data_access.find_csv_record(
        "dataset/port_calls.csv", "call_id", call_id
    )
    if not port_call:
        return {"error": "Port call not found."}

    manifest_path = f"dataset/manifests/{call_id.lower()}.json"
    try:
        manifest = data_access.load_json(manifest_path)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"error": "Manifest unavailable."}

    if not manifest or "event_codes" not in manifest:
        return {"error": "Manifest contains no event data."}

    event_codes = manifest.get("event_codes", [])
    sequence, length = get_longest_stable_sequence(event_codes)

    return {
        "call_id": call_id,
        "all_codes": event_codes,
        "stable_sequence": sequence,
        "length": length,
    }

# task 8 
def assess_weather_risk():
    _, vessel_id, _ = data_access.validate_vessel_input()
    reference_date = data_access.validate_date_input()
    uppcoming_call = find_earliest_call(vessel_id, reference_date)
    if not uppcoming_call:
        print("No upcoming port calls found")
    else:
        port_code = uppcoming_call["port_code"]
        arrival_date = uppcoming_call["arrival_date"]
    
    row = data_access.find_csv_record("/dataset/weather.csv", "port_code", port_code)


