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
