# Medication Schedule Optimizer

This project optimizes medication schedules based on input prescriptions and interaction data.

## Directory Structure

- `data/`: Contains the data files (`interactions.xlsx`, `db_drug_interactions.csv`, `drug_data.csv`)
- `inputs/`: Input files (e.g., `input.txt`) describing the patient's prescriptions
- `src/`:
  - `main.py`: Contains the `MedicationScheduleOptimizer` class which orchestrates the solution.
  - `parser.py`: Parsing functions.
  - `utils.py`: Helper functions for data loading, interaction modeling, scheduling, and output.
- `tests/`: Contains unit tests.


```text
swe-project/
├─ data/
│  ├─ interactions.xlsx
│  ├─ db_drug_interactions.csv
│  └─ drug_data.csv
├─ inputs/
│  └─ input.txt
├─ src/
│  ├─ main.py      # Contains the main class orchestrating the solution
│  ├─ parser.py    # Parsing functions
│  ├─ utils.py     # Helper functions (data loading, interaction building, scheduling, output formatting)
├─ tests/
│  ├─ test_parser.py
│  └─ ...
└─ readme.md
```

## Usage

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Codebase Summary

**main.py**  
- Contains `MedicationScheduleOptimizer` class, the main entry point for running the workflow:
  - `run()`: Handles user interaction and triggers all steps.
  - `load_and_prepare_data()`: Loads datasets and preprocesses them.
  - `parse_input_prescriptions(input_str=None)`: Parses user input or file input for prescriptions.
  - `optimize_schedule()`: Runs the constraint solver to find a feasible medication schedule.
  - `display_schedule()`: Prints the optimized schedule with formatting and warnings.

**parser.py**  
- `parse_prescriptions(input_str: str)`: Converts raw textual prescriptions into structured data (a list of dictionaries).

**utils.py**  
- `load_data(interactions_xlsx, db_interactions_csv, drug_data_csv)`: Loads drug and interaction data.
- `build_interaction_dict(df1, df2)`: Builds a dictionary of drug-to-drug interactions.
- `create_schedule(prescriptions, interactions)`: Uses a constraint solver to assign times to each prescription, avoiding conflicts.
- `print_schedule(schedule, drug_data)`: Formats and prints the resulting schedule as a table, including warnings.

**tests/test_parser.py**  
- Tests the parser functionality, e.g.:
  - `TestParser.test_parse_prescriptions()`: Verifies correct parsing of textual input into prescription objects.

**readme.md**  
- Provides instructions, directory structure, and workflow details.

**data/**  
- Contains interaction and drug datasets.

**inputs/**  
- Contains default input files (like `input.txt`) for testing.

**tests/**  
- Directory for test files.

