# Medication Schedule Optimizer
## 20875 – Software Engineering 2024
### MSc in Artificial Intelligence Bocconi

This project optimizes medication schedules based on input prescriptions and interaction data.

## Directory Structure

- `data/`: Contains the data files (`interactions.xlsx`, `db_drug_interactions.csv`, `drug_data.csv`)
- `inputs/`: Input files (e.g., `input.txt`) describing the patient's prescriptions
- `src/`:
  - `main.py`: Contains the `MedicationScheduleOptimizer` class which orchestrates the solution.
  - `parser.py`: Parsing functions.
  - `utils.py`: Helper functions for data loading, interaction modeling, scheduling, and output.
- `tests/`: Contains unit tests and test files such as eda.py


```text
swe-project/
├─ data/
│  ├─ interactions_text.csv
│  └─ drug_data_1.csv
├─ inputs/
│  └─ input.txt
├─ src/
│  ├─ main.py      # Contains the main class
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

## Database information

### drug_data_1.csv: Comprehensive Drug Information Dataset (https://www.kaggle.com/datasets/anoopjohny/comprehensive-drug-information-dataset)

The "Pharmaceutical Product Data Repository" is a comprehensive dataset containing detailed information about a wide range of pharmaceutical drugs. This dataset encompasses various attributes related to each drug, including drug names, generic names, drug classes, indications, dosage forms, strengths, routes of administration, mechanisms of action, side effects, contraindications, interactions, warnings, precautions, pregnancy categories, storage conditions, manufacturers, approval dates, availability status (prescription or over-the-counter), National Drug Code (NDC) numbers, and prices.

sample:
```
Drug ID,Drug Name,Generic Name,Drug Class,Indications,Dosage Form,Strength,Route of Administration,Mechanism of Action,Side Effects,Contraindications,Interactions,Warnings and Precautions,Pregnancy Category,Storage Conditions,Manufacturer,Approval Date,Availability,NDC,Price
1,Aspirin,Acetylsalicylic Acid,Analgesic,Headache,Tablet,325 mg,Oral,Inhibits prostaglandin synthesis,Stomach irritation,Allergy to NSAIDs,Anticoagulants: increased bleeding risk,Gastric ulcers: risk of bleeding,Category C,Room temperature,PharmaCorp,15-01-2022,OTC,12345678901,5.99
2,Amoxicillin,Amoxicillin,Antibiotic,Bacterial Infections,Capsule,500 mg,Oral,Inhibits bacterial cell wall synthesis,Nausea, Allergic reactions,Penicillin: reduced efficacy,Take with food to reduce stomach upset,Category B,Room temperature,MediPharm,20-11-2021,Prescription,23456789012,12.49
```


### interactions_text.csv: Drug-Drug Interactions (https://www.kaggle.com/datasets/mghobashy/drug-drug-interactions)

This dataset provides a comprehensive collection of drug-drug interactions (DDIs) intended for research in predicting and understanding complex interaction relationships between drugs. It is sourced from the Drug Bank database and is designed to support multi-task learning approaches in the domain of bioinformatics and pharmacology.

Feature Details:
Drug 1: Name of the first drug in the interaction.
Drug 2: Name of the second drug in the interaction.
Interaction Description: Detailed description of the interaction between the two drugs.

Source: The dataset is derived from the datasets provided by the team at TDCommons

sample:
```
Drug 1,Drug 2,Interaction Description
Trioxsalen,Verteporfin,Trioxsalen may increase the photosensitizing activities of Verteporfin.
Aminolevulinic acid,Verteporfin,Aminolevulinic acid may increase the photosensitizing activities of Verteporfin.
```