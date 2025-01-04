import sys
from parser import parse_prescriptions
from utils import load_data, build_interaction_dict, create_schedule, print_schedule

class MedicationScheduleOptimizer:
    def __init__(self, data_dir="data", input_dir="inputs"):
        self.data_dir = data_dir
        self.input_dir = input_dir
        self.interactions = {}
        self.prescriptions = []
        self.schedule = {}
        self.drug_data = None
        self.diet = {}

    def load_and_prepare_data(self):
        db_interactions_csv = "data/common_interactions.csv"
        drug_data_csv = "data/common_drugs.csv"
        #interactions_effects = "data/interactions_effects.csv"
        df_db_interactions, df_drug_data = load_data(db_interactions_csv, drug_data_csv)
        self.interactions = build_interaction_dict(df_db_interactions)
        self.drug_data = df_drug_data

    def parse_input_prescriptions(self, input_str=None):
        if input_str is None:
            input_file = f"{self.input_dir}/input.txt"
            try:
                with open(input_file, 'r') as f:
                    input_str = f.read()
            except FileNotFoundError:
                print(f"Input file {input_file} not found.")
                sys.exit(1)

        self.prescriptions, self.diet = parse_prescriptions(input_str)
        for pres in self.prescriptions:
            pres['name'] = pres['name'].title() # normalising drug names by capitalising the first letter
        if not self.prescriptions:
            print("No prescriptions found in input. Please check the format.")
            sys.exit(1)
        self.validate_drug_names() # validate drug names against known drugs

    def validate_drug_names(self):
        if self.drug_data is not None and 'Drug Name' in self.drug_data.columns:
            known_drugs = set(self.drug_data['Drug Name'].str.title())
            for pres in self.prescriptions:
                if pres['name'] not in known_drugs:
                    print(f"Unknown drug: {pres['name']}. Please correct the name or update your datasets.")
                    sys.exit(1)
        else:
            print("Warning: Drug data not available or missing 'Drug Name' column, cannot validate drug names.")
            # Not exiting here, but we could if desired.

    def optimize_schedule(self):
        self.schedule = create_schedule(self.prescriptions, self.interactions, self.drug_data, self.diet)
        if self.schedule is None:
            print("\nUnable to find a feasible schedule. Please adjust constraints or inputs.")
        else:
            print("\nSchedule optimised successfully.")

    def display_schedule(self):
        if self.schedule:
            print_schedule(self.schedule, self.drug_data)
        else:
            print("\nNo schedule available to display.")

    def run(self):
        while True:
            # print("Please choose:")
            # print("[1] Use input.txt")
            # print("[2] Enter prescriptions manually")
            # print("[q] Quit")

            # choice = input("> ").strip().lower()

            choice = '1' # temporarily disable user input

            if choice == '2':
                print("\nEnter prescriptions in the format:")
                print('"DrugName: once/twice/thrice daily (optional_times)"')
                print("For example:")
                print('  Aspirin: once daily (morning)')
                print('  Ibuprofen: twice daily')
                print('  Metformin: twice daily (morning, evening)')
                print("\nInclude a 'Diet:' line if desired, e.g.:")
                print('  Diet: breakfast 8 am; lunch 1 pm; dinner 8 pm')
                print("Press Enter on an empty line to run.\n")

                lines = []
                while True:
                    line = input("> ").strip()
                    if line == "":
                        break
                    lines.append(line)
                if not lines:
                    print("No input given. Exiting.")
                    sys.exit(0)
                input_str = "\n".join(lines)
                self.load_and_prepare_data()
                self.parse_input_prescriptions(input_str=input_str)
                break

            elif choice == '1':
                self.load_and_prepare_data()
                self.parse_input_prescriptions()
                print("Using input from file:\n")
                with open(f"{self.input_dir}/input.txt", "r") as f:
                    print(f.read())  # Print input file content if using file-based input
                break

            elif choice in ['quit', 'q']:
                print("Exiting.")
                sys.exit(0)

            else:
                print("Invalid input. Please type '1', '2', or 'q'.")

        # Display interactions
        risky_pairs = []
        if not self.interactions:
            print("No interactions found between prescribed drugs.")
        else:
            print("Interactions between drugs:")
            for pair, interaction in self.interactions.items():
                drug1, drug2 = pair
                prescribed_drugs = {pres['name'].title() for pres in self.prescriptions}
                if drug1 in prescribed_drugs and drug2 in prescribed_drugs:
                    print(f" - {drug1} and {drug2}: {interaction['description']}")
                    if interaction['risk'] == 1:  # Check for risky interactions
                        risky_pairs.append(f"{drug1} and {drug2}")

        # Print risky combinations if any
        if risky_pairs:
            print("\nRisky drug combinations are:")
            for pair in risky_pairs:
                print(f" - {pair}")
        else:
            print("\nNo risky drug combinations identified.")

        self.optimize_schedule()
        self.display_schedule()


if __name__ == "__main__":
    optimizer = MedicationScheduleOptimizer()
    optimizer.run()