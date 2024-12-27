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
    interactions = {}
    for _, row in df_db_interactions.iterrows():
        dA, dB = row['Drug 1'], row['Drug 2']
        pair = tuple(sorted([dA, dB]))
        if pair not in interactions:
            interactions[pair] = {"risk": "Unknown", "description": row['Interaction Description']}
    return interactions

def get_warnings_map(drug_data):
    warnings_map = {}
    if drug_data is not None and 'Drug Name' in drug_data.columns and 'Warnings and Precautions' in drug_data.columns:
        for _, row in drug_data.iterrows():
            drug_name = rozw['Drug Name'].title()
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
                if "without food" or "empty stomach" or "before a meal" in instructions_lower:
                    return True
    return False

def drug_requires_food(drug_name, drug_data): #to accomodate the cases in which the drug must be taken with food 
    if (drug_data is not None and 
        'Drug Name' in drug_data.columns and 
        'Warnings and Precautions' in drug_data.columns):
        row = drug_data[drug_data['Drug Name'].str.title() == drug_name.title()]
        if not row.empty:
            instructions = row.iloc[0]['Warnings and Precautions']
            if isinstance(instructions, str):
                instructions_lower = instructions.lower()
                if "with food" or "with meals" in instructions_lower:
                    return True
    return False

def create_schedule(prescriptions, interactions, drug_data, diet):
    model = cp_model.CpModel()
    times = ["08:00", "12:00", "16:00", "20:00"]
    drug_vars = {}
    for i, pres in enumerate(prescriptions): # Create variables: each dose of each prescription
        for d_idx in range(pres['frequency']):
            for t in times:
                drug_vars[(i, d_idx, t)] = model.NewBoolVar(f"drug_{i}_dose_{d_idx}_{t}")
    for i, pres in enumerate(prescriptions): # each dose once
        for d_idx in range(pres['frequency']):
            model.Add(sum(drug_vars[(i, d_idx, t)] for t in times) == 1)
    # Interaction constraints logic TBA
    pref_map = {"morning":"08:00","noon":"12:00","evening":"16:00","night":"20:00"}
    for i, pres in enumerate(prescriptions):
        if pres.get('preferred_times'):
            for pt in pres['preferred_times']:
                pt_l = pt.lower()
                if pt_l in pref_map:
                    slot = pref_map[pt_l]
                    model.Add(sum(drug_vars[(i, d, slot)] for d in range(pres['frequency'])) >= 1)
    # Without food constraints
    meal_times = set(diet.values()) if diet else set()
    for i, pres in enumerate(prescriptions):
        if drug_requires_without_food(pres['name'], drug_data):
            for d_idx in range(pres['frequency']):
                for mt in meal_times:
                    if mt in times:
                        model.Add(drug_vars[(i, d_idx, mt)] == 0)
    # With food constraints
    for i, pres in enumerate(prescriptions): # I don't know if it is ok (I think it may cause problems if my is not in times)
        if drug_requires_food(pres['name'], drug_data):
            for d_idx in range(pres['frequency']):
                model.Add(sum(drug_vars[(i, d_idx, mt)] for mt in meal_times if mt in times) == 1)
    # No two doses of the same drug at the same time (already ensured by each dose once, but let's keep it)
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
                for d_idx in range(pres['frequency']):
                    if solver.Value(drug_vars[(i,d_idx,t)]) == 1:
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
                combined_warnings.append("") # blank line between drugs
            wrapped = textwrap.wrap(w, width=max_width) or ["None"]
            combined_warnings.extend([f"{d_title}: {wrapped[0]}"] + wrapped[1:])
        all_rows.append([[t], [drug_list], combined_warnings])
    col_widths = [0,0,0]
    for row in all_rows:
        for i, col_lines in enumerate(row):
            for line in col_lines:
                if len(line) > col_widths[i]:
                    col_widths[i] = len(line)
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
                line += " " + cell_line + " "*(col_widths[i]-len(cell_line)+1) + "|"
            print(line)
        print(sep_line())