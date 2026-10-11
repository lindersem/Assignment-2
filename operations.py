"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import json
import data_access
from datetime import datetime


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
