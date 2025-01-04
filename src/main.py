import sys
from parser import parse_prescriptions
from utils import load_data, build_interaction_dict, create_schedule, print_schedule, save_schedule_to_file

choices_enabled = 0

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
        
        # Validate meal times after parsing the diet
        self.validate_meal_times()

        for pres in self.prescriptions:
            pres['name'] = pres['name'].title()  # Normalize drug names by capitalizing the first letter
        if not self.prescriptions:
            print("No prescriptions found in input. Please check the format.")
            sys.exit(1)
        self.validate_drug_names()  # Validate drug names against known drugs

    def validate_meal_times(self):
        """ Ensure that meals are placed in the correct time categories. """
        time_preferences = {
            "morning": ("06:00", "12:00"),
            "afternoon": ("12:01", "17:59"),
            "evening": ("18:00", "22:00")
        }

        for meal, time in self.diet.items():
            if meal == "breakfast" and not (time_preferences["morning"][0] <= time <= time_preferences["morning"][1]):
                print(f"Invalid breakfast time {time}. Breakfast must be in the morning (06:00 - 12:00).")
                sys.exit(1)
            elif meal == "lunch" and not (time_preferences["afternoon"][0] <= time <= time_preferences["afternoon"][1]):
                print(f"Invalid lunch time {time}. Lunch must be in the afternoon (12:01 - 17:59).")
                sys.exit(1)
            elif meal == "dinner" and not (time_preferences["evening"][0] <= time <= time_preferences["evening"][1]):
                print(f"Invalid dinner time {time}. Dinner must be in the evening (18:00 - 22:00).")
                sys.exit(1)


    def optimize_schedule(self):
        self.schedule = create_schedule(self.prescriptions, self.interactions, self.drug_data, self.diet)
        if self.schedule is None:
            print("\nUnable to find a feasible schedule. Please adjust constraints or inputs.")
        else:
            print("\nSchedule optimised successfully.")
    
    def display_schedule(self):
     if self.schedule:
        print_schedule(self.schedule, self.drug_data)
        if choices_enabled == 1:
            choice = input("Do you want the schedule to be saved in a .txt file? (y/n): ").strip().lower()
        else:
            choice = 'n'
        if choice in ['y', 'yes']:
            filename = input("Please write the desired name for the file (include .txt): ").strip()
            if not filename.endswith(".txt"):
                print("Invalid file name. The schedule was not saved.")
            else:
                save_schedule_to_file(self.schedule, self.drug_data, filename=filename)
        elif choice in ['n', 'no']:
            print("Schedule not saved.")
        else:
            print("Invalid choice. Schedule not saved.")
     else:
        print("No schedule available to display.")

    def run(self):
        while True:
            print("\033[1mWelcome to the Medication Schedule Optimizer!\033[0m")
            print("Please choose:")
            print("[1] Use input.txt")
            print("[2] Enter prescriptions manually")
            print("[q] Quit\n")
            if choices_enabled == 1:
                choice = input("> ").strip().lower()
            else:
                choice = '1'

            if choice == '2':
                print("\nEnter prescriptions in the format:")
                print('"DrugName: once/twice/thrice daily (optional_times)"')
                print("Allowed optional_times are: morning, afternoon, evening ")
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
                print("Using input from file:")
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
        undesirable_pairs = []
        if len(self.prescriptions) > 1:
            if not self.interactions:
                print("\nNo interactions found between prescribed drugs.")
            else:
                print("\nInteractions between drugs:")
                for pair, interaction in self.interactions.items():
                    drug1, drug2 = pair
                    prescribed_drugs = {pres['name'].title() for pres in self.prescriptions}
                    if drug1 in prescribed_drugs and drug2 in prescribed_drugs:
                        description = interaction['description']
                        # Make drug names bold in the description
                        description = description.replace(drug1, f"\033[1m{drug1}\033[0m")
                        description = description.replace(drug2, f"\033[1m{drug2}\033[0m")
                        print(f" - {description}")
                        if interaction['risk'] == 1:  # Check for risky interactions
                            risky_pairs.append(f"{drug1} and {drug2}")
                        elif interaction['undesirable'] == 1:
                            undesirable_pairs.append(f"{drug1} and {drug2}")  
            if risky_pairs:
                print("\nRisky drug combinations are:")
                for pair in risky_pairs:
                    pair = pair.replace(pair.split()[0], f"\033[1m{pair.split()[0]}\033[0m")    
                    pair = pair.replace(pair.split()[2], f"\033[1m{pair.split()[2]}\033[0m")
                    print(f" - {pair}")
            if undesirable_pairs:
                print("\nUndesirable drug combinations are:")
                for pair in undesirable_pairs:
                    pair = pair.replace(pair.split()[0], f"\033[1m{pair.split()[0]}\033[0m")    
                    pair = pair.replace(pair.split()[2], f"\033[1m{pair.split()[2]}\033[0m")
                    print(f" - {pair}")
            if not risky_pairs and not undesirable_pairs:
                print("\nNo risky or undesirable drug combinations identified.")

        self.optimize_schedule()
        self.display_schedule()

if __name__ == "__main__":
    optimizer = MedicationScheduleOptimizer()
    optimizer.run()