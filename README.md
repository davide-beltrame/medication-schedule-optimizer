# Medication Schedule Optimizer
## 20875 – Software Engineering 2024
### MSc in Artificial Intelligence Bocconi

## Overview
The **Medication Schedule Optimizer** is a tool designed to streamline medication scheduling for patients by avoiding harmful drug interactions and considering dietary constraints. By leveraging detailed drug interaction datasets and constraint-solving algorithms, this project aims to:
- Provide optimal medication schedules tailored to individual patient needs and dietary indications.
- Minimize the risk associated with drug-drug interactions.
- Incorporate food-related constraints for drugs that require specific consumption conditions.

The overarching objective of this project is to assist healthcare professionals and patients in managing the challenges of complex medication regimens.

## Directory Structure

- `data/`: Contains the data files (`interactions_text.csv`, `drug_data_1.csv`), sourced from external databases.
- `inputs/`: Contains example patient prescription input files (e.g., `input.txt`).
- `src/`:
  - `main.py`: Contains the `MedicationScheduleOptimizer` class which orchestrates the solution.
  - `parser.py`: Parsing functions.
  - `utils.py`: Helper functions for data loading, interaction modeling, scheduling, and output.
- `tests/`: Includes unit tests and exploratory data analysis (`eda.py`) to understand dataset properties and structure.

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

Before running the program, ensure that all required dependencies are installed. Follow these steps:  

1. Install Requirements  
  Open a terminal in the project directory.  
  Run the following command to install all necessary Python packages:  
   ```bash
   pip install -r requirements.txt
   ```

2. Run the program 
  To start the application, execute the main script using Python. A user-friendly interface will guide you through the process.
  Run the following command: 
   ```python src/main.py
   ```

After running the command, the program will display the following prompt:
  Do you want to enter prescriptions now? (y/n/quit) 
If you enter y:
   You will be prompted to input prescription details. The program will display instructions about the required format before collecting the input.
If you enter n:
  A default input file from the inputs/ directory will be used to test the functionality of the application.
If you enter quit:
  The program will terminate without processing any input.

  Once the input is processed, the program generates an optimized medication schedule that will be displayed in the terminal.

## Codebase Summary

**main.py**: Orchestrates the entire scheduling process, from data preparation to displaying results.    
- Contains `MedicationScheduleOptimizer` class, the main entry point for running the workflow:
  - `run()`: Handles user interaction and triggers all steps.
  - `load_and_prepare_data()`: Loads datasets and preprocesses them.
  - `parse_input_prescriptions(input_str=None)`: Parses user input or file input for prescriptions.
  - `optimize_schedule()`: Runs the constraint solver to find a feasible medication schedule.
  - `display_schedule()`: Prints the optimized schedule with formatting and warnings.

**parser.py**  
- `parse_prescriptions(input_str: str)`: Converts raw textual prescriptions into structured data (a list of dictionaries).

**utils.py**: Houses supporting functions for data handling, interaction modeling, and schedule optimization.

- `load_data(interactions_xlsx, db_interactions_csv, drug_data_csv)`: Loads drug and interaction data.  
- `build_interaction_dict(df1, df2)`: Builds a dictionary of drug-to-drug interactions.  
- `get_warnings_map(drug_data)`: Extracts warnings from the dataset for each drug.  
- `drug_requires_without_food(drug_name, drug_data)`, `drug_requires_food(drug_name, drug_data)`: Handles food interaction constraints by identifying drugs that require consumption with or without food.  
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

## Database Information

### drug_data_1.csv: Comprehensive Drug Information Dataset
[Source: Kaggle](https://www.kaggle.com/datasets/anoopjohny/comprehensive-drug-information-dataset)

The "Pharmaceutical Product Data Repository" is a comprehensive dataset containing detailed information about a wide range of pharmaceutical drugs. This dataset encompasses various attributes related to each drug, including drug names, generic names, drug classes, indications, dosage forms, strengths, routes of administration, mechanisms of action, side effects, contraindications, interactions, warnings, precautions, pregnancy categories, storage conditions, manufacturers, approval dates, availability status (prescription or over-the-counter), National Drug Code (NDC) numbers, and prices.

**Sample:**
```csv
Drug ID,Drug Name,Generic Name,Drug Class,Indications,Dosage Form,Strength,Route of Administration,Mechanism of Action,Side Effects,Contraindications,Interactions,Warnings and Precautions,Pregnancy Category,Storage Conditions,Manufacturer,Approval Date,Availability,NDC,Price
1,Aspirin,Acetylsalicylic Acid,Analgesic,Headache,Tablet,325 mg,Oral,Inhibits prostaglandin synthesis,Stomach irritation,Allergy to NSAIDs,Anticoagulants: increased bleeding risk,Gastric ulcers: risk of bleeding,Category C,Room temperature,PharmaCorp,15-01-2022,OTC,12345678901,5.99
2,Amoxicillin,Amoxicillin,Antibiotic,Bacterial Infections,Capsule,500 mg,Oral,Inhibits bacterial cell wall synthesis,Nausea, Allergic reactions,Penicillin: reduced efficacy,Take with food to reduce stomach upset,Category B,Room temperature,MediPharm,20-11-2021,Prescription,23456789012,12.49
```

### interactions_text.csv: Drug-Drug Interactions
[Source: Kaggle](https://www.kaggle.com/datasets/mghobashy/drug-drug-interactions)

This dataset provides a comprehensive collection of drug-drug interactions (DDIs) designed for research in predicting and understanding complex interaction relationships between drugs.

**Feature Details:**
- **Drug 1**: Name of the first drug in the interaction.
- **Drug 2**: Name of the second drug in the interaction.
- **Interaction Description**: Detailed description of the interaction between the two drugs.

**Sample:**
```csv
Drug 1,Drug 2,Interaction Description
Trioxsalen,Verteporfin,Trioxsalen may increase the photosensitizing activities of Verteporfin.
Aminolevulinic acid,Verteporfin,Aminolevulinic acid may increase the photosensitizing activities of Verteporfin.
```

## Example Usage

Below is an example of the application in action:
```text
davidebeltrame@MB-Pro-di-Davide swe-project % python src/main.py
Do you want to enter prescriptions now? (y/n/quit): n
Using input from file:

Prednisone: twice daily (morning)
Metformin: twice daily (morning)
Levofloxacin: thrice daily
Ibuprofen: once daily (afternoon)
Diet: breakfast 10 am; lunch 1 pm; dinner 8 pm

Interactions between drugs are:

Levofloxacin and Prednisone: The risk or severity of adverse effects can be increased when Prednisone is combined with Levofloxacin.
Levofloxacin and Metformin: Metformin may increase the hypoglycemic activities of Levofloxacin.
Ibuprofen and Levofloxacin: Ibuprofen may increase the neuroexcitatory activities of Levofloxacin.
Ibuprofen and Prednisone: The risk or severity of adverse effects can be increased when Ibuprofen is combined with Prednisone.
Metformin and Prednisone: The therapeutic efficacy of Metformin can be decreased when used in combination with Prednisone.

Schedule optimized successfully.
+-------+-----------------------+-------------------------------------------------------------+
| Time  |         Drugs         |                          Warnings                           |
+-------+-----------------------+-------------------------------------------------------------+
| 06:00 | Levofloxacin          | Levofloxacin: Take 2 hours before or 6 hours after antacids |
+-------+-----------------------+-------------------------------------------------------------+
| 10:00 | Prednisone, Metformin | Prednisone: Take with food or milk                          |
|       |                       |                                                             |
|       |                       | Metformin: Take with meals                                  |
+-------+-----------------------+-------------------------------------------------------------+
| 17:00 | Levofloxacin          | Levofloxacin: Take 2 hours before or 6 hours after antacids |
+-------+-----------------------+-------------------------------------------------------------+
| 19:00 | Ibuprofen             | Ibuprofen: Anticoagulants: increased bleeding risk          |
+-------+-----------------------+-------------------------------------------------------------+
| 20:00 | Prednisone, Metformin | Prednisone: Take with food or milk                          |
|       |                       |                                                             |
|       |                       | Metformin: Take with meals                                  |
+-------+-----------------------+-------------------------------------------------------------+
| 22:00 | Levofloxacin          | Levofloxacin: Take 2 hours before or 6 hours after antacids |
+-------+-----------------------+-------------------------------------------------------------+
```

As shown above, the application assists doctors or patients in scheduling medications correctly based on the prescription.
