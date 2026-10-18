HARBORFLOW PORT INTELLIGENCE CONSOLE - TEAM README

Run instructions
----------------
Command: py main.py (or: python main.py)
Python version tested: 3.14.7

Team members and concrete contributions
---------------------------------------
Name: Linder
Contribution:
- Task 4 (Export a customer operations profile)
- Task 5 (Find port calls by month)
- Task 6
- testing

Name: Monika
Contribution:
- Task 2
- Task 7
- Task 9
- documentation, test-strategy, testing

Name: Olha
Contribution:
- Task 3
- flowchart
- testing

Name: Youyue (Avery)
Contribution:
- Task 0
- Task 1
- Task 8
- code cleanup, function generalization
- testing

Architecture
------------
main.py responsibilities:
    - program's entry point
    - manages the menu (in main())
    - gets input from the user
    - calls functions from operations, data_access
    - calls formatted printing functions 
data_access.py responsibilities:
    - reads and writes to JSON and CSV files
    - loads all files from a folder
    - handles search and record lookup
    - checks if cache needs updating
operations.py responsibilities:
    - calls functions from data_access, text_tools
    - finds and filters port calls (by date and by month)
    - builds manifests by matching port calls to shipments 
    - classifies shipments into categories using hazard, temperature, and weight
    - generates customer profiles based on shipment totals and destinations
    - assesses weather risk by matching upcoming calls to forecasts
    - generates recommendations using wind, wave, and rain thresholds
    - implements search and indexing logic for incidents 
text_tools.py responsibilities:
    - removes sensitive info from text (sanitization())
    - cleans and splits text into words for searching
    - finds the longest stable sequence of events

File and error-handling design
------------------------------
How paths are resolved:
    - relative paths from the project root
    - for path construction: os.path.join was used
How malformed or missing input is handled:
    - user input validated with try-except blocks and validation functions
    - file loading uses try-except for FileNotFoundError and json.JSONDecodeError
    - skips malformed records or returns None
How generated files are updated safely:
    - "read-modify-write" pattern for CSVs
    - check target directories exist

Known limitations
-----------------
    - Load large datasets entirely into memory, which may impact performance (eg.load_every_json())
    - Printing and error message formatting may differ task-by-task.
    - JSON structure limitation: The program assumes that each JSON file contains a single dictionary (JSON object). Other JSON structures, such as arrays, are not supported.