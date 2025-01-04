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

    # Exact phrase for adverse effects
    risk_phrase = "the risk or severity of adverse effects can be increased when"

    interactions = {}
    for _, row in df_db_interactions.iterrows():
        dA, dB = row['Drug 1'], row['Drug 2']
        pair = tuple(sorted([dA, dB]))

        desc = row['Interaction Description']
        desc_lower = desc.lower()

        # Flag as risky only if the exact phrase is present
        is_risky = risk_phrase in desc_lower
        interactions[pair] = {
            "risk": 1 if is_risky else 0,
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

def drug_requires_without_food(drug_name, drug_data):
    if drug_data is not None and 'Drug Name' in drug_data.columns and 'Instructions' in drug_data.columns:
        row = drug_data[drug_data['Drug Name'].str.title() == drug_name.title()]
        if not row.empty:
            instructions = row.iloc[0]['Warnings and Precautions']
            if isinstance(instructions, str):
                instructions_lower = instructions.lower()
                # If *any* of these phrases is in the instructions, True
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

def create_schedule(prescriptions, interactions, drug_data, diet):
    model = cp_model.CpModel()
    base_times = [f"{hour:02d}:00" for hour in range(6, 23)]
    meal_times = set(diet.values()) if diet else set()
    times = sorted(set(base_times).union(meal_times))

    # Variables
    drug_vars = {}
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        for d_idx in range(freq):
            for t in times:
                drug_vars[(i, d_idx, t)] = model.NewBoolVar(f"drug_{i}_dose_{d_idx}_{t}")

    # Each dose must be placed exactly once
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        for d_idx in range(freq):
            model.Add(sum(drug_vars[(i, d_idx, t)] for t in times) == 1)

    # Ensure doses of the same drug are spaced evenly
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        interval = len(times) // freq
        for d_idx in range(freq - 1):
            model.Add(
                sum(
                    drug_vars[(i, d_idx, t)] * times.index(t)
                    for t in times
                )
                + interval <=
                sum(
                    drug_vars[(i, d_idx + 1, t)] * times.index(t)
                    for t in times
                )
            )

    # With food => must align with meal times
    for i, pres in enumerate(prescriptions):
        if drug_requires_food(pres['name'], drug_data):
            for d_idx in range(pres['frequency']):
                model.Add(sum(drug_vars[(i, d_idx, t)] for t in meal_times) == 1)

    # Without food => avoid meal times
    for i, pres in enumerate(prescriptions):
        if drug_requires_without_food(pres['name'], drug_data):
            for d_idx in range(pres['frequency']):
                for t in meal_times:
                    model.Add(drug_vars[(i, d_idx, t)] == 0)

    # Avoid scheduling risky drugs at the same time
    for pair, interaction in interactions.items():
        if interaction['risk'] == 1:
            drug1, drug2 = pair
            drug1_indices = [i for i, pres in enumerate(prescriptions) if pres['name'] == drug1]
            drug2_indices = [i for i, pres in enumerate(prescriptions) if pres['name'] == drug2]

            for i1 in drug1_indices:
                for i2 in drug2_indices:
                    for t in times:
                        model.Add(drug_vars[(i1, 0, t)] + drug_vars[(i2, 0, t)] <= 1)

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
