import pandas as pd
import textwrap
from ortools.sat.python import cp_model

def load_data(interactions_xlsx, db_interactions_csv, drug_data_csv):
    df_interactions = pd.read_excel(interactions_xlsx)
    df_db_interactions = pd.read_csv(db_interactions_csv)
    df_drug_data = pd.read_csv(drug_data_csv)
    return df_interactions, df_db_interactions, df_drug_data

def build_interaction_dict(df1, df2):
    interactions = {}
    # Normalize drug names
    df1['Drug_A'] = df1['Drug_A'].str.title()
    df1['Drug_B'] = df1['Drug_B'].str.title()
    for _, row in df1.iterrows():
        dA, dB = row['Drug_A'], row['Drug_B']
        key = tuple(sorted([dA, dB]))
        interactions[key] = {
            "risk": row['Risk_Level'],
            "description": row['Interaction']
        }
    df2['Drug 1'] = df2['Drug 1'].str.title()
    df2['Drug 2'] = df2['Drug 2'].str.title()
    for _, row in df2.iterrows():
        dA, dB = row['Drug 1'], row['Drug 2']
        key = tuple(sorted([dA, dB]))
        if key not in interactions:
            interactions[key] = {
                "risk": "Unknown",
                "description": row['Interaction Description']
            }
    return interactions

def create_schedule(prescriptions, interactions):
    model = cp_model.CpModel()
    times = ["morning", "noon", "evening", "night"]
    
    drug_vars = {}
    for i, pres in enumerate(prescriptions):
        for dose_idx in range(pres['frequency']):
            for t in times:
                drug_vars[(i, dose_idx, t)] = model.NewBoolVar(f"drug_{i}_dose_{dose_idx}_{t}")

    # Each dose must be taken exactly once
    for i, pres in enumerate(prescriptions):
        for dose_idx in range(pres['frequency']):
            model.Add(sum(drug_vars[(i, dose_idx, t)] for t in times) == 1)

    # Interaction constraints: if high risk, can’t be same slot
    for (dA, dB), details in interactions.items():
        if details['risk'].lower() == 'high':
            idxA = [i for i, p in enumerate(prescriptions) if p['name'].title() == dA]
            idxB = [i for i, p in enumerate(prescriptions) if p['name'].title() == dB]
            for iA in idxA:
                for iB in idxB:
                    for doseA in range(prescriptions[iA]['frequency']):
                        for doseB in range(prescriptions[iB]['frequency']):
                            for t in times:
                                model.Add(drug_vars[(iA, doseA, t)] + drug_vars[(iB, doseB, t)] <= 1)

    # Preferred times constraint: if given
    # Here we simply ensure that at least one dose matches each preferred time
    # This could be made more strict depending on your requirements
    for i, pres in enumerate(prescriptions):
        for pref_time in pres['preferred_times']:
            # require that at least one dose of this drug matches pref_time
            model.Add(sum(drug_vars[(i, d, pref_time)] for d in range(pres['frequency'])) >= 1)

    # Objective: For now, just a feasible solution
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
        return schedule
    else:
        return None

def print_schedule(schedule, drug_data):
    # Map times to hours
    time_mapping = {
        "morning": "08:00 AM",
        "noon": "12:00 PM",
        "evening": "06:00 PM",
        "night": "10:00 PM"
    }
    
    # Filter out empty time slots
    filtered_schedule = {t: schedule[t] for t in schedule if schedule[t]}
    if not filtered_schedule:
        print("No medications scheduled.")
        return

    # Build warnings map
    warnings_map = {}
    if drug_data is not None and 'Drug Name' in drug_data.columns and 'Warnings and Precautions' in drug_data.columns:
        for _, row in drug_data.iterrows():
            drug_name = row['Drug Name'].title()
            warning = row['Warnings and Precautions']
            warnings_map[drug_name] = warning if isinstance(warning, str) else "None"
    else:
        warnings_map = {}

    headers = ["Time", "Drugs", "Warnings"]

    # Prepare rows as lists of lists, but warnings will be multi-line
    all_rows = []
    
    # Define max width for wrapping warnings
    max_warning_width = 60

    for t, drugs in filtered_schedule.items():
        display_time = time_mapping.get(t, t)  
        drug_list = ", ".join(drugs)

        # Prepare warnings line(s)
        slot_warnings_lines = []
        for d in drugs:
            d_title = d.title()
            w = warnings_map.get(d_title, "None")
            # Wrap the warning text
            wrapped = textwrap.wrap(w, width=max_warning_width)
            if not wrapped:
                wrapped = ["None"]
            # Add the drug name prefix to the first line of the wrapped text
            slot_warnings_lines.append([f"{d_title}: {wrapped[0]}"] + wrapped[1:])

        # Flatten the warnings from all drugs into a single list of lines
        # Each drug's warning lines are separated by a blank line for clarity
        combined_warnings_lines = []
        for i, drug_lines in enumerate(slot_warnings_lines):
            if i > 0:
                combined_warnings_lines.append("")  # blank line between different drugs' warnings
            combined_warnings_lines.extend(drug_lines)

        # Store the row
        all_rows.append([ [display_time], [drug_list], combined_warnings_lines ])

    # Now we have rows as [[time_lines],[drug_lines],[warning_lines]]
    # In this case, time and drugs have single-line entries, but warnings can have multiple lines.
    # We need to figure out column widths and the max row height.

    # Calculate column widths based on the longest line in each column
    col_widths = [0, 0, 0]
    for row in all_rows:
        for i, col_lines in enumerate(row):
            for line in col_lines:
                if len(line) > col_widths[i]:
                    col_widths[i] = len(line)

    # Determine row heights (max number of lines in each column of a row)
    # The row height is the max number of lines in any column of that row
    row_heights = []
    for row in all_rows:
        heights = [len(col) for col in row]  # number of lines in each column
        row_heights.append(max(heights))

    def sep_line():
        return "+" + "+".join("-"*(w+2) for w in col_widths) + "+"

    def format_header(headers):
        # Single line headers, center them
        line = "|"
        for i, h in enumerate(headers):
            space = col_widths[i] - len(h)
            left_pad = space // 2
            right_pad = space - left_pad
            line += " " + (" " * left_pad) + h + (" " * right_pad) + " |"
        return line

    print(sep_line())
    print(format_header(headers))
    print(sep_line())

    # Print each row with its lines
    for row, height in zip(all_rows, row_heights):
        # row = [ [time_lines], [drug_lines], [warnings_lines] ]
        for line_idx in range(height):
            line = "|"
            for i, col_lines in enumerate(row):
                if line_idx < len(col_lines):
                    cell_line = col_lines[line_idx]
                else:
                    cell_line = ""  # no line here, just blank
                line += " " + cell_line + " "*(col_widths[i] - len(cell_line) + 1) + "|"
            print(line)
        print(sep_line())
