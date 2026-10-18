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
main.py responsibilities: menu and orchestration
data_access.py responsibilities: JSON/CSV loading, validation and paths
operations.py responsibilities: manifests, classification, forecasts and exports
text_tools.py responsibilities: regex sanitization, sequence and search index

File and error-handling design
------------------------------
How paths are resolved:
How malformed or missing input is handled:
How generated files are updated safely:

Known limitations
-----------------
Write "None known" or describe each known limitation.
* JSON structure limitation: The program assumes that each JSON file contains a single dictionary (JSON object). Other JSON structures, such as arrays, are not supported.