import pandas as pd
import textwrap
from ortools.sat.python import cp_model

RISK_PRIORITY = {"Unknown": 0}

def load_data(db_interactions_csv, drug_data_csv):
    df_db_interactions = pd.read_csv(db_interactions_csv)
    df_drug_data = pd.read_csv(drug_data_csv)
    return df_db_interactions, df_drug_data

def build_interaction_dict(df_db_interactions): # interactions_text.csv has no explicit risk, assume Unknown
    df_db_interactions['Drug 1'] = df_db_interactions['Drug 1'].str.title() # Convert drug names to title case for consistency
    df_db_interactions['Drug 2'] = df_db_interactions['Drug 2'].str.title()

    # Very simple risk keywords
    risk_keywords = ["increase", "contraindicated", "severe", "serious", "major", "fatal"]

    interactions = {}
    for _, row in df_db_interactions.iterrows():
        dA, dB = row['Drug 1'], row['Drug 2']
        pair = tuple(sorted([dA, dB]))

        desc = row['Interaction Description']
        desc_lower = desc.lower()

        is_risky = any(kw in desc_lower for kw in risk_keywords)
        risk_value = 1 if is_risky else 0

        if pair not in interactions:
            interactions[pair] = {
                "risk": risk_value if risk_value else "Unknown",
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
    base_times = ["06:00", "08:00", "12:00", "16:00", "20:00", "22:00"]
    meal_times = set(diet.values()) if diet else set()
    times = sorted(set(base_times).union(meal_times))

    # Build a dynamic pref_map based on the final 'times' list
    # You can tweak the hour ranges to fit your needs
    def hour_of(t_str):
        return int(t_str.split(":")[0])

    dynamic_pref_map = {
        "morning": [t for t in times if 6 <= hour_of(t) < 12],
        "noon":    [t for t in times if hour_of(t) == 12],
        "evening": [t for t in times if 13 <= hour_of(t) < 19],
        "night":   [t for t in times if hour_of(t) >= 19],
    }

    drug_vars = {}
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        for d_idx in range(freq):
            for t in times:
                drug_vars[(i, d_idx, t)] = model.NewBoolVar(f"drug_{i}_dose_{d_idx}_{t}")

    # Each dose once
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        for d_idx in range(freq):
            model.Add(sum(drug_vars[(i, d_idx, t)] for t in times) == 1)

    # Preferred times - must be placed in at least one time from the dynamic map
    for i, pres in enumerate(prescriptions):
        if pres.get('preferred_times'):
            freq = pres['frequency']
            for pt in pres['preferred_times']:
                pt_l = pt.lower()
                if pt_l in dynamic_pref_map:
                    valid_slots = dynamic_pref_map[pt_l]
                    # At least one dose must be in these valid slots
                    model.Add(
                        sum(
                            drug_vars[(i, d_idx, slot)]
                            for d_idx in range(freq)
                            for slot in valid_slots
                        ) >= 1
                    )

    # Without food => not at mealtimes
    for i, pres in enumerate(prescriptions):
        if drug_requires_without_food(pres['name'], drug_data):
            freq = pres['frequency']
            for d_idx in range(freq):
                for mt in meal_times:
                    model.Add(drug_vars[(i, d_idx, mt)] == 0)

    # With food => must be at one of the meal_times
    for i, pres in enumerate(prescriptions):
        if drug_requires_food(pres['name'], drug_data):
            freq = pres['frequency']
            for d_idx in range(freq):
                model.Add(sum(drug_vars[(i, d_idx, mt)] for mt in meal_times) == 1)

    # No two doses of the same drug at the same time
    for i, pres in enumerate(prescriptions):
        freq = pres['frequency']
        if freq > 1:
            for d1 in range(freq):
                for d2 in range(d1+1, freq):
                    for t in times:
                        model.Add(drug_vars[(i, d1, t)] + drug_vars[(i, d2, t)] <= 1)

    model.Minimize(0)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        schedule = {t: [] for t in times}
        for t in times:
            for i, pres in enumerate(prescriptions):
                freq = pres['frequency']
                for d_idx in range(freq):
                    if solver.Value(drug_vars[(i, d_idx, t)]) == 1:
                        schedule[t].append(pres['name'])
        return {t: v for t, v in schedule.items() if v}
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
