import pandas as pd
import textwrap
from ortools.sat.python import cp_model

RISK_PRIORITY = {"Unknown": 0}

def load_data(db_interactions_csv, drug_data_csv):
    df_db_interactions = pd.read_csv(db_interactions_csv)
    df_drug_data = pd.read_csv(drug_data_csv)
    return df_db_interactions, df_drug_data

def build_interaction_dict(df_db_interactions):
    df_db_interactions['Drug 1'] = df_db_interactions['Drug 1'].str.title()
    df_db_interactions['Drug 2'] = df_db_interactions['Drug 2'].str.title()

    risk_phrase = "the risk or severity of adverse effects can be increased when"
    undesirable_phrase = "therapeutic efficacy of"

    interactions = {}
    for _, row in df_db_interactions.iterrows():
        dA, dB = row['Drug 1'], row['Drug 2']
        pair = tuple(sorted([dA, dB]))

        desc = row['Interaction Description']
        desc_lower = desc.lower()

        is_risky = risk_phrase in desc_lower
        is_undesirable = undesirable_phrase in desc_lower

        interactions[pair] = {
            "risk": 1 if is_risky else 0,
            "undesirable": 1 if is_undesirable else 0,
            "description": desc
        }
    return interactions

def get_warnings_map(drug_data):
    warnings_map = {}
    if drug_data is not None and 'Drug Name' in drug_data.columns and 'Warnings and Precautions' in drug_data.columns:
        for _, row in drug_data.iterrows():
            drug_name = row['Drug Name'].title()
            w = row['Warnings and Precautions']
            warnings_map[drug_name] = w if isinstance(w, str) else "None"
    return warnings_map

def drug_requires_no_food(drug_name, drug_data):
    if drug_data is not None and 'Drug Name' in drug_data.columns and 'Warnings and Precautions' in drug_data.columns:
        row = drug_data[drug_data['Drug Name'].str.title() == drug_name.title()]
        if not row.empty:
            instructions = row.iloc[0]['Warnings and Precautions']
            if isinstance(instructions, str):
                instructions_lower = instructions.lower()
                if "without food" in instructions_lower or \
                   "empty stomach" in instructions_lower or \
                   "before a meal" in instructions_lower:
                    return True
    return False

def drug_requires_food(drug_name, drug_data):
    if (drug_data is not None and
        'Drug Name' in drug_data.columns and
        'Warnings and Precautions' in drug_data.columns):
        row = drug_data[drug_data['Drug Name'].str.title() == drug_name.title()]
        if not row.empty:
            instructions = row.iloc[0]['Warnings and Precautions']
            if isinstance(instructions, str):
                instructions_lower = instructions.lower()
                if "with food" in instructions_lower or "with meals" in instructions_lower:
                    return True
    return False

def get_max_separation_slots(time_preferences, frequency):
    """ 
    Get maximally spaced slots across different parts of the day.
    E.g., for 2 doses, morning and evening; for 3 doses, morning, afternoon, and evening.
    """
    slot_groups = [time_preferences["morning"], time_preferences["afternoon"], time_preferences["evening"]]
    available_groups = [group for group in slot_groups if len(group) > 0]
    
    if frequency > len(available_groups):  # Not enough groups to fully separate
        return None

    chosen_slots = []
    for idx in range(frequency):
        group = available_groups[idx % len(available_groups)]
        chosen_slots.append(group[0])  # Pick the first available time in each group
    return chosen_slots

def handle_diet_constraints(prescriptions, drug_vars, drug_data, diet, model):
    meal_times = set(diet.values()) if diet else {"08:00", "13:00", "19:00"}
    food_drugs = []  # Collect drugs that require food
    no_food_drugs = []  # Collect drugs that require no food

    # With food => must align with meal times
    for i, pres in enumerate(prescriptions):
        if drug_requires_food(pres['name'], drug_data):
            for d_idx in range(pres['frequency']):
                model.Add(sum(drug_vars[(i, d_idx, t)] for t in meal_times) == 1)
            if not diet:  # Add drug name only if default meal times are being used
                food_drugs.append(pres['name'])

    # Without food => must avoid meal times
    for i, pres in enumerate(prescriptions):
        if drug_requires_no_food(pres['name'], drug_data):
            for d_idx in range(pres['frequency']):
                model.Add(sum(drug_vars[(i, d_idx, t)] for t in meal_times) == 0)  # No dose should happen at meal times
            if not diet:  # Add drug name only if default meal times are being used
                no_food_drugs.append(pres['name']) 

    # Print notes with all food-related and no-food-related drugs
    if food_drugs:
        print(f"\n\033[1mNote:\033[0m Using default meal times (08:00, 13:00, 19:00) for drugs that require food: {', '.join(food_drugs)}.")
    if no_food_drugs:
        print(f"\033[1mNote:\033[0m Avoiding default meal times (08:00, 13:00, 19:00) for drugs that require no food: {', '.join(no_food_drugs)}.")

def add_interaction_constraints(model, prescriptions, interactions, drug_vars, times):
    """
    Add constraints for risky and undesirable drug combinations.
    - Risky combinations: Must be respected for feasibility.
    - Undesirable combinations: Attempt to enforce but silently ignore if unfeasible.
    """
    for pair, interaction in interactions.items():
        drug1, drug2 = pair
        drug1_indices = [i for i, pres in enumerate(prescriptions) if pres['name'] == drug1]
        drug2_indices = [i for i, pres in enumerate(prescriptions) if pres['name'] == drug2]

        for i1 in drug1_indices:
            for i2 in drug2_indices:
                for t in times:
                    if interaction['risk'] == 1:  # Risky interaction: strict constraint
                        model.Add(drug_vars[(i1, 0, t)] + drug_vars[(i2, 0, t)] <= 1)
                    elif interaction.get('undesirable', 0) == 1:  # Undesirable interaction: attempt but ignore if infeasible
                        try:
                            model.Add(drug_vars[(i1, 0, t)] + drug_vars[(i2, 0, t)] <= 1)
                        except Exception:
                            # Silently ignore this undesirable constraint if it causes infeasibility
                            pass

def create_schedule(prescriptions, interactions, drug_data, diet):
    model = cp_model.CpModel()
    base_times = [f"{hour:02d}:00" for hour in range(6, 23)]
    meal_times = set(diet.values()) if diet else {"08:00", "13:00", "19:00"}
    times = sorted(set(base_times).union(meal_times))

    # Variables
    drug_vars = {}
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        for d_idx in range(freq):
            for t in times:
                drug_vars[(i, d_idx, t)] = model.NewBoolVar(f"drug_{i}_dose_{d_idx}_{t}")

    # Time-of-day preferences (pre-defined slots)
    time_preferences = {
        "morning": [t for t in times if "06:00" <= t <= "12:00"],
        "afternoon": [t for t in times if "12:01" <= t <= "17:59"],
        "evening": [t for t in times if "18:00" <= t <= "22:00"]
    }

    # Ensure doses of the same drug are spaced out properly
    for i, pres in enumerate(prescriptions):
        time_of_day = pres.get("preferred_times", [])
        freq = pres['frequency']

        if time_of_day:
            time_window = time_preferences.get(time_of_day[0].lower(), times)
        else:
            time_window = times

        if drug_requires_food(pres['name'], drug_data):
            time_window = sorted(set(time_window).intersection(meal_times))
        elif drug_requires_no_food(pres['name'], drug_data):
            time_window = sorted(set(time_window) - meal_times)

        for d_idx in range(freq):
            model.Add(sum(drug_vars[(i, d_idx, t)] for t in time_window) == 1)

        # Ensure no more than one dose of the same drug in a single time slot
        for t in times:
            model.Add(sum(drug_vars[(i, d_idx, t)] for d_idx in range(freq)) <= 1)

        # Ensure spacing between doses
        if freq > 1:
            for d_idx in range(freq - 1):
                model.Add(
                    sum(drug_vars[(i, d_idx, t)] * times.index(t) for t in time_window) + 2 <=
                    sum(drug_vars[(i, d_idx + 1, t)] * times.index(t) for t in time_window)
                )

    # Add diet-related constraints and print notes
    handle_diet_constraints(prescriptions, drug_vars, drug_data, diet, model)

    # Try to add interaction constraints
    add_interaction_constraints(model, prescriptions, interactions, drug_vars, times)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Output schedule
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        schedule = {t: [] for t in times}
        for t in times:
            for i, pres in enumerate(prescriptions):
                freq = pres['frequency']
                for d_idx in range(freq):
                    if solver.Value(drug_vars[(i, d_idx, t)]) == 1:
                        schedule[t].append(pres['name'])
        return {time: drugs for time, drugs in schedule.items() if drugs}
    else:
        return None

def print_schedule(schedule, drug_data):
    if not schedule:
        print("No medications scheduled.")
        return
    warnings_map = get_warnings_map(drug_data)
    headers = ["Time", "Drugs", "Warnings"]
    max_width = 60
    all_rows = []

    for t, drugs in schedule.items():
        drug_list = ", ".join(drugs)
        combined_warnings = []
        for d in drugs:
            d_title = d.title()
            w = warnings_map.get(d_title, "None")
            if combined_warnings:
                combined_warnings.append("")  # blank line between drugs
            from textwrap import wrap
            wrapped = wrap(w, width=max_width) or ["None"]
            combined_warnings.extend([f"{d_title}: {wrapped[0]}"] + wrapped[1:])
        all_rows.append([[t], [drug_list], combined_warnings])

    col_widths = [0, 0, 0]
    for row in all_rows:
        for i, col_lines in enumerate(row):
            for line in col_lines:
                col_widths[i] = max(col_widths[i], len(line))

    row_heights = [max(len(col) for col in row) for row in all_rows]

    def sep_line():
        return "+" + "+".join("-"*(w+2) for w in col_widths) + "+"

    def format_header(hs):
        line = "|"
        for i, h in enumerate(hs):
            space = col_widths[i] - len(h)
            left_pad = space // 2
            right_pad = space - left_pad
            line += " " + (" " * left_pad) + h + (" " * right_pad) + " |"
        return line

    print(sep_line())
    print(format_header(headers))
    print(sep_line())

    for row, height in zip(all_rows, row_heights):
        for line_idx in range(height):
            line = "|"
            for i, col_lines in enumerate(row):
                cell_line = col_lines[line_idx] if line_idx < len(col_lines) else ""
                line += " " + cell_line + " "*(col_widths[i] - len(cell_line) + 1) + "|"
            print(line)
        print(sep_line())

def save_schedule_to_file(schedule, drug_data, filename="schedule.txt"):
    if not schedule:
        print("No schedule available to save.")
        return
    warnings_map = get_warnings_map(drug_data)
    max_width = 60

    with open(filename, 'w') as f:
        f.write("Medication Schedule\n")
        f.write("=" * 20 + "\n")
        for t, drugs in schedule.items():
            f.write(f"\nTime: {t}\n")
            f.write(f"Drugs: {', '.join(drugs)}\n")
            f.write("Warnings:\n")
            for d in drugs:
                d_title = d.title()
                warnings = warnings_map.get(d_title, "None")
                wrapped = textwrap.wrap(warnings, width=max_width) or ["None"]
                f.write(f"  {d_title}: {wrapped[0]}\n")
                for line in wrapped[1:]:
                    f.write(f"    {line}\n")
            f.write("\n")
        print(f"Schedule saved to {filename}")