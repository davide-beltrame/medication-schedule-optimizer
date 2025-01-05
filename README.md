# Medication Schedule Optimizer
## 20875 – Software Engineering 2024
### MSc in Artificial Intelligence – Bocconi University
### Final Project by:
- **Davide Beltrame 3306906**
- **Francesca Dessalvi 3325685**
---
## Overview
The **Medication Schedule Optimizer** is a practical tool designed to simplify the process of creating medication schedules for patients. It helps avoid harmful drug interactions and respects dietary requirements. Using drug interaction data and a constraint-solving approach, the project aims to:

- Create personalized medication schedules based on patient prescriptions and meal times.
- Reduce the risk of adverse drug-drug interactions.
- Handle medications that need to be taken with or without food.

The goal is to support healthcare providers and patients in managing complex medication plans more easily and safely.

## Directory Structure

- `data/`: Contains the drug interaction data files (`interactions_text.csv`, `drug_data_1.csv`) sourced from external databases, as well as simplified versions (`common_interactions.csv`, `common_drugs.csv`) for testing and debugging.
- `inputs/`: Includes sample patient prescription files (e.g., `input.txt`) to test the program.
- `src/`:
  - `main.py`: The main script that runs the program, containing the `MedicationScheduleOptimizer` class, which manages the entire process.
  - `parser.py`: Handles the parsing of prescription inputs.
  - `utils.py`: Provides helper functions for loading data, managing drug interactions, creating schedules, and formatting the output.
- `tests/`: Contains unit tests and exploratory scripts (`eda.py`) for analyzing and validating the datasets.

```text
swe-project/
├─ data/
│  ├─ interactions_text.csv
│  └─ drug_data_1.csv
├─ inputs/
│  └─ input.txt
├─ src/
│  ├─ main.py    
│  ├─ parser.py 
│  ├─ utils.py     
├─ tests/
│  ├─ eda.py
│  └─ ...
└─ README.md
```

## Usage  

Before running the program, make sure you have installed all the required dependencies. Follow these steps:

1. Install Requirements  

  Open a terminal in the project directory and run the following command to install the necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the program 

  To start the application, run the main script using Python. The program will guide you through the steps with a user-friendly interface:
   ```bash
   python src/main.py
   ```

## Codebase Summary

### **`main.py`**
This script orchestrates the entire medication scheduling process, from loading data to displaying the results.  
Key components:
- **`MedicationScheduleOptimizer`**: The main class that handles the workflow.
  - `__init__(self, data_dir="data", input_dir="inputs")`: Initializes directories and variables for data and prescriptions.
  - `load_and_prepare_data()`: Loads datasets (drug information and interactions) and prepares them for use.
  - `parse_input_prescriptions(input_str=None)`: Reads prescriptions either from `input.txt` or a manual input.
  - `validate_drug_names()`: Checks if prescribed drug names exist in the loaded dataset.
  - `validate_meal_times()`: Ensures that meal times (breakfast, lunch, dinner) are within valid ranges.
  - `optimize_schedule()`: Uses the constraint solver to create an optimized medication schedule.
  - `display_schedule()`: Prints the generated schedule, formatted with relevant warnings.
  - `run()`: Main method that handles user interactions, runs the full optimization, and manages the program flow.

---

### **`parser.py`**
This module parses the prescription input and extracts prescription details and dietary information.
- `parse_prescriptions(input_str: str)`: Converts raw prescription text into structured data (a list of dictionaries with drug names, frequencies, and preferred times).
- `convert_time_to_24h(time_str: str)`: Converts "8 am" or "1 pm" formats to 24-hour times ("08:00", "13:00").

---

### **`utils.py`**
Contains helper functions for loading data, handling interactions, and creating the schedule.
- `load_data(db_interactions_csv, drug_data_csv)`: Reads CSV files containing drug information and interaction data.
- `build_interaction_dict(df_db_interactions)`: Creates a dictionary mapping drug pairs to their interaction details.
- `get_warnings_map(drug_data)`: Maps drug names to their warnings and precautions.
- `drug_requires_no_food(drug_name, drug_data)`, `drug_requires_food(drug_name, drug_data)`: Determine if a drug must be taken without or with food.
- `handle_diet_constraints(prescriptions, drug_vars, drug_data, diet, model)`: Ensures that food-related drug constraints align with meal times.
- `add_interaction_constraints(model, prescriptions, interactions, drug_vars, times)`: Adds constraints to avoid risky or undesirable drug combinations.
- `create_schedule(prescriptions, interactions, drug_data, diet)`: Uses Google OR-Tools' constraint programming to generate a feasible medication schedule.
- `print_schedule(schedule, drug_data)`: Prints the schedule in a formatted table.
- `save_schedule_to_file(schedule, drug_data, filename)`: Saves the schedule to a `.txt` file if requested.

---

### **`tests/eda.py`**
This script provides exploratory data analysis (EDA) for understanding the dataset structure and validating its contents.
- `basic_dataset_info(df_drug, df_interactions)`: Prints basic statistics of the drug and interaction datasets.
- `analyze_interactions(df_interactions)`: Identifies unique types of interactions and their frequencies.
- `interaction_description_stats(df_interactions)`: Displays length statistics of interaction descriptions.
- `merged_drug_info(df_drug, df_interactions)`: Merges datasets to check overlaps and distributions of drug classes.
- `build_subset_1(drugs_csv, interactions_csv, output_csv)`: Creates a small dataset subset with interactions involving the first three drugs for testing purposes.

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

## Step-by-step

The **Medication Schedule Optimizer** works in a step-by-step process to create a personalized medication schedule while considering drug interactions and dietary constraints. 

1. **Starting the Program**:  
   When you run the program (`python src/main.py`), it welcomes you with a menu. You can either:
   - Use a random input file  from the `inputs/` folder.
   - Enter your prescriptions manually during the session.

2. **Reading the Input**:  
   The program reads the input file or manual input line by line. Each line contains details like the drug name, how many times a day it should be taken, and optional preferred times (e.g., morning, afternoon, evening). It also reads your meal times (e.g., breakfast at 8 am, lunch at 1 pm).

3. **Validating the Input**:  
   - The program checks that all drug names are valid by comparing them against the drug database.
   - It makes sure that meal times are reasonable (e.g., breakfast should be in the morning).
   - If any issues are found (e.g., unknown drug names or invalid times), the program provides clear feedback and exits to prevent errors.

4. **Checking Drug Interactions**:  
   The program cross-checks the drugs in your prescription for known interactions:
   - **Risky combinations**: Pairs of drugs that can cause serious side effects when taken together.
   - **Undesirable combinations**: Pairs of drugs that reduce each other’s effectiveness.

   If interactions are found, the program lists them and highlights them for your awareness.

5. **Creating the Schedule**:  
   - The program uses a "constraint solver" (a smart algorithm) to figure out the best times to take each medication.
   - It spaces out doses throughout the day, ensures medications are taken with or without food as needed, and avoids overlapping times for interacting drugs.
   - If a feasible schedule can’t be found (due to too many conflicting constraints), it suggests reviewing the prescriptions or input data.

6. **Displaying the Schedule**:  
   Once the schedule is created:
   - It prints a table showing what medications to take at specific times, along with warnings (e.g., "take with food").
   - You can choose to save the schedule as a text file for later reference.

7. **Saving the Schedule**:  
   If you opt to save the schedule, the program will create a `.txt` file with the details neatly formatted.

To sum it up, the program reads your prescription and meal details, checks for interactions, and optimizes your medication times to avoid conflicts and follow dietary rules. It then presents an easy-to-read schedule to help you take your medications safely and efficiently.

## Example Usage

Below is an  example of the application in action:

```bash
davidebeltrame@MB-Pro-di-Davide swe-project % python src/main.py
Welcome to the Medication Schedule Optimizer!
Please choose:
[1] Use input.txt
[2] Enter prescriptions manually
[q] Quit
Using input from file:
Prednisone: once daily (morning)
Metformin: twice daily
Levofloxacin: thrice daily
Ibuprofen: twice daily (afternoon)
Enalapril: once daily (evening)
Diet: breakfast 7 am; lunch 1 pm; dinner 8 pm
Interactions between drugs:
 - The risk or severity of adverse effects can be increased when Prednisone is combined with Levofloxacin.
 - Metformin may increase the hypoglycemic activities of Levofloxacin.
 - Ibuprofen may increase the neuroexcitatory activities of Levofloxacin.
 - The risk or severity of adverse effects can be increased when Ibuprofen is combined with Prednisone.
 - The risk or severity of adverse effects can be increased when Enalapril is combined with Ibuprofen.
 - The therapeutic efficacy of Metformin can be decreased when used in combination with Prednisone.
Risky drug combinations:
 - Levofloxacin and Prednisone
 - Ibuprofen and Prednisone
 - Enalapril and Ibuprofen
Undesirable drug combinations:
 - Metformin and Prednisone
Schedule optimized successfully:
+-------+-------------------------+-------------------------------------------------------------+
| Time  |          Drugs           |                          Warnings                           |
+-------+-------------------------+-------------------------------------------------------------+
| 07:00 | Prednisone               | Prednisone: Take with food or milk                          |
+-------+-------------------------+-------------------------------------------------------------+
| 13:00 | Metformin, Ibuprofen     | Metformin: Take with meals                                  |
|       |                          |                                                             |
|       |                          | Ibuprofen: Anticoagulants: increased bleeding risk          |
+-------+-------------------------+-------------------------------------------------------------+
| 14:00 | Levofloxacin             | Levofloxacin: Take 2 hours before or 6 hours after antacids |
+-------+-------------------------+-------------------------------------------------------------+
| 17:00 | Ibuprofen                | Ibuprofen: Anticoagulants: increased bleeding risk          |
+-------+-------------------------+-------------------------------------------------------------+
| 18:00 | Levofloxacin, Enalapril  | Levofloxacin: Take 2 hours before or 6 hours after antacids |
|       |                          |                                                             |
|       |                          | Enalapril: Take on an empty stomach                         |
+-------+-------------------------+-------------------------------------------------------------+
| 19:00 | Levofloxacin             | Levofloxacin: Take 2 hours before or 6 hours after antacids |
+-------+-------------------------+-------------------------------------------------------------+
| 20:00 | Metformin                | Metformin: Take with meals                                  |
+-------+-------------------------+-------------------------------------------------------------+
```