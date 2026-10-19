import os
import data_access, operations
from datetime import datetime
import text_tools


def display_menu():
    console_name = "HARBORFLOW PORT INTELLIGENCE"
    console_menu = """1. List registered vessels
2. Inspect a vessel manifest
3. Identify priority cargo
4. Export a customer operations profile 
5. Find port calls by month
6. Sanitize an incident report
7. Analyze the longest stable event sequence 
8. Assess weather risk for upcoming calls 
9. Search incident reports
10. Close console"""
    print(f"""{console_name}\n{console_menu}""")


# print task 1
def list_registered_vessels(valid_vessels, skipped_vessel_file):
    print("Register HarborFlow vessels: ")

    for valid_vessel in valid_vessels:
        list_vessels = f"- {valid_vessel['name']}  |  IMO {valid_vessel['imo']}  |  {valid_vessel['capacity_teu']:,} TEU"
        print(list_vessels)

    print(f"Skipped vessel files: {skipped_vessel_file}")


# print task 2
def display_vessel_selection_list(vessels):
    print("Registered vessels:")
    for vessel in vessels:
        print(f"- {vessel['name']}")


# print task 2
def output_vessel_manifest(official_vessel_name, call_id, call_date, manifest_data):
    print(f"Vessel name: {official_vessel_name}")

    date = datetime.strptime(call_date, "%Y-%m-%d")
    formatted_date = date.strftime("%d %B %Y")
    print(f"Manifest for {official_vessel_name} | Call {call_id} | {formatted_date}")
    for i, ship in enumerate(manifest_data["shipments"], 1):
        if "missing" in ship:
            print(f"{i}. {ship['shipment_id']} | MISSING RECORD")
        else:
            cargo_type = ship.get("cargo_type", "NOT PROVIDED")
            customer = ship.get("customer", "Unknown")
            weight = ship.get("weight_kg", 0)
            print(
                f"{i}. {ship['shipment_id']} | {customer} | {weight} kg | {cargo_type}"
            )
    print(f"Declared shipments: {manifest_data['declared_count']}")
    print(f"Resolved weight: {manifest_data['total_weight']:.2f} kg")
    print(f"Missing shipment records: {manifest_data['missing_count']}")


# print task 7
def print_stable_sequence_results(result):
    all_codes = result["all_codes"]
    sequence = result["stable_sequence"]
    length = result["length"]

    print(f"Event codes: {','.join(all_codes)}")
    print(f"Longest stable sequence length: {length}")
    print(f"Sequence: {' -> '.join(sequence)}")


# print task 8
def display_assess_weather_risk():
    results = operations.assess_weather_risk()
    if results is None:
        return
    for result in results:
        display_assessment = f"""{result["vessel_name"]} | {result["port_code"]} | {result["arrival_date"]}
Wind: {result["wind_kmh"]} km/h | Rain: {result["precipitation_mm"]} mm | Waves: {result["wave_height_m"]} m
Recommendation: {" ".join(result["recommendations"])}"""
        print(display_assessment)


# print task 9
def display_incident_search_results(query, matches):
    print(f"\nMatches for '{query}':")
    print("-" * 60)

    if not matches:
        print("No matching incident reports found.")
    else:
        for incident_id, score, title in matches:
            print(f"- {incident_id} | score {score} | {title}")

    print("-" * 60)


def main():
    """Run the HarborFlow Port Intelligence Console."""

    running = True

    while running:
        display_menu()

        try:
            selected_service = int(input("Select service: "))
        except ValueError:
            print("Error - Select a service from 1 to 10.")
            continue

        if selected_service == 1:
            # List registered vessels
            valid_vessels, skipped_vessel_file = data_access.load_vessels(
                "dataset/vessels/"
            )
            list_registered_vessels(valid_vessels, skipped_vessel_file)

        elif selected_service == 2:
            # Inspect a vessel manifest
            vessels = data_access.list_registered_vessels("dataset/vessels/")
            display_vessel_selection_list(vessels)
            vessel_input = input("Vessel name: ").strip().lower()
            vessel = data_access.get_vessel_by_name(vessel_input)
            if not vessel:
                print("Vessel not found.")
                continue
            else:
                official_vessel_name = vessel["name"]
                vessel_id = vessel["vessel_id"]
                date_is_valid = False
                while not date_is_valid:
                    date_input = input("Reference date: ").strip()
                    if data_access.is_valid_date(date_input):
                        date_is_valid = True
                    else:
                        print("Error - Date must use YYYY-MM-DD")

                call = operations.find_earliest_call(vessel_id, date_input)
                if not call:
                    print("No upcoming port calls found.")
                    continue
                else:
                    call_id = call["call_id"]
                    call_date = call["arrival_date"]
                    manifest = operations.resolve_manifest(call["call_id"])
                    if not manifest:
                        print("Manifest unavailable.")
                        continue
                    else:
                        output_vessel_manifest(
                            official_vessel_name, call_id, call_date, manifest
                        )

        elif selected_service == 3:
            # Identify priority cargo
            call_id_input = input("Enter Call ID: ").strip()

            # Call the orchestration function from operations.py
            result = operations.process_priority_cargo(call_id_input)

            # Handle errors returned from operations.py
            if "error" in result:
                print(result["error"])
            else:
                # Print the success output
                print(f"\nPriority Cargo Report for Call ID: {result['call_id']}")
                print("-" * 80)

                for item in result["shipments"]:
                    print(
                        f"Shipment ID: {item['shipment_id']} | Category: {item['category']} | Reason: {item['reason']}"
                    )

                print("-" * 80)
                print("Category Totals:")
                for category, count in result["counts"].items():
                    print(f"- {category}: {count}")

        elif selected_service == 4:
            # Export a customer operations profile
            customer_input = input("Customer name: ")
            operations.export_customer_operations_profile(customer_input)

        elif selected_service == 5:
            # Find port calls by month
            while True:
                month_input = input("Month (1-12): ")
                try:
                    month = int(month_input)
                    if 1 <= month <= 12:
                        operations.find_port_calls_by_month(month)
                        break
                    else:
                        print("Error - Enter a month from 1 to 12.")
                except ValueError:
                    print("Error - Enter a month from 1 to 12.")

        elif selected_service == 6:
            # Sanitize an incident report
            incidents = data_access.load_every_json("dataset/incidents")
            sorted_incidents = sorted(incidents, key=lambda x: x["title"].lower())
            i = 1

            for incident in sorted_incidents:
                print(f"{i}. {incident["title"]}")
                i += 1

            while True:
                try:
                    incident_number = int(input("Incident number: "))
                    if incident_number > 0 and incident_number <= len(sorted_incidents):
                        sanitized_text = text_tools.sanitize(
                            sorted_incidents[incident_number - 1]["report"]
                        )
                        if (
                            sanitized_text
                            == sorted_incidents[incident_number - 1]["report"]
                        ):
                            print("Incident contains no share-sensitive identifiers.")
                        else:
                            file_path = f"exports/sanitized/{sorted_incidents[incident_number-1]["incident_id"]}-sanitized.txt"

                            # extract the directory portion and create it if missing
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)

                            # open and create the file
                            with open(file_path, "w") as f:
                                f.write(f"{sanitized_text}")
                        break
                    else:
                        print("Error - Select a listed incident.")

                except ValueError:
                    print("Error - Select a listed incident.")
            pass

        elif selected_service == 7:
            # Analyze the longest stable event sequence
            call_id_from_user = input("Port call ID: ").strip()
            result = operations.get_sequence_for_port_call(call_id_from_user)

            if "error" in result:
                print(f"Error - {result['error']}")
            else:
                print_stable_sequence_results(result)

        elif selected_service == 8:
            display_assess_weather_risk()

        elif selected_service == 9:
            # Search incident reports
            query_input = input("Search incident reports: ").strip()
            if not query_input:
                print("Error - Please enter search keywords.")
                continue

            results = operations.search_incidents(query_input)

            display_incident_search_results(query_input, results)

        elif selected_service == 10:
            # Close console
            running = False
            print("Console closed. HarborFlow operational data remains safe.")

        else:
            print("Error - Select a service from 1 to 10.")

    pass


if __name__ == "__main__":
    main()
