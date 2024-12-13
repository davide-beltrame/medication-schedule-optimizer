import sys
from pathlib import Path
from parser import parse_prescriptions
from utils import (
    load_data,
    build_interaction_dict,
    create_schedule,
    print_schedule
)


class MedicationScheduleOptimizer:
    def __init__(self, data_dir="data", input_dir="inputs"):
        self.data_dir = data_dir
        self.input_dir = input_dir
        self.interactions = {}
        self.prescriptions = []
        self.schedule = {}
        self.drug_data = None

    def load_and_prepare_data(self):
        interactions_xlsx = Path(self.data_dir, "interactions.xlsx")
        db_interactions_csv = Path(self.data_dir, "db_drug_interactions.csv")
        drug_data_csv = Path(self.data_dir, "drug_data.csv")
        df_interactions, df_db_interactions, df_drug_data = load_data(
            interactions_xlsx,
            db_interactions_csv,
            drug_data_csv
        )
        self.interactions = build_interaction_dict(df_interactions, df_db_interactions)
        self.drug_data = df_drug_data

    def parse_input_prescriptions(self, input_str=None):
        if input_str is not None:
            self.prescriptions = parse_prescriptions(input_str)
        else:
            input_path = Path(self.input_dir, "input.txt")
            if not input_path.exists():
                print(f"Input file {input_path} not found.")
                sys.exit(1)
            with open(input_path, 'r') as f:
                input_str = f.read()
            self.prescriptions = parse_prescriptions(input_str)

        if not self.prescriptions:
            print("No prescriptions found in input. Please check the format.")
            sys.exit(1)

    def optimize_schedule(self):
        self.schedule = create_schedule(self.prescriptions, self.interactions)
        if self.schedule is None:
            print("Unable to find a feasible schedule. Please adjust constraints or inputs.")
        else:
            print("Schedule optimized successfully.")

    def display_schedule(self):
        if self.schedule:
            print_schedule(self.schedule, self.drug_data)
        else:
            print("No schedule available to display.")

    def run(self):
      while True:
            choice = input("Do you want to enter prescriptions now? (y/n/quit): ").strip().lower()
            if choice in ['y', 'yes']:
                  print("\nEnter prescriptions in the format:")
                  print('"DrugName: once/twice/thrice daily (optional_times)"')
                  print("Times are optional. Examples:")
                  print('  "Warfarin: once daily (morning)"')
                  print('  "Ibuprofen: thrice daily"')
                  print('  "Metformin: twice daily (morning, evening)"')
                  print("\nAvailable frequencies: once, twice, thrice daily")
                  print("Preferred times: morning, noon, evening, night (comma-separated if multiple)")
                  print("\nExample drugs: Aspirin, Ibuprofen, Metformin, Warfarin, Lisinopril, Amoxicillin, Paracetamol, Atorvastatin, Omeprazole, Alprazolam")
                  print("Press Enter on an empty line to finish.\n")

                  lines = []
                  while True:
                        line = input("> ").strip()
                        if line == "":
                              break
                        lines.append(line)
                  input_str = "\n".join(lines)
                  if not lines:
                        print("No input given. Exiting.")
                        sys.exit(0)
                  self.load_and_prepare_data()
                  self.parse_input_prescriptions(input_str=input_str)
                  break
            elif choice in ['n', 'no']:
                  self.load_and_prepare_data()
                  self.parse_input_prescriptions()
                  break
            elif choice in ['quit', 'q']:
                  print("Exiting.")
                  sys.exit(0)
            else:
                  print("Invalid input. Please type 'y', 'n', or 'quit'.")

      self.optimize_schedule()
      self.display_schedule()


if __name__ == "__main__":
    optimizer = MedicationScheduleOptimizer()
    optimizer.run()
