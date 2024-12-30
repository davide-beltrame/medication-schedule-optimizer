import re

def parse_prescriptions(input_str: str):
    lines = input_str.strip().split('\n')
    prescriptions = []
    diet = {}
    freq_map = {"once":1, "twice":2, "thrice":3}
    pattern = r"^(.*?):\s*(once|twice|thrice)\s+daily(?:\s*\((.*?)\))?$"

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue # Ignore comment lines
        if line.lower().startswith("diet:"):
            diet_line = line[len("Diet:"):].strip()
            meal_entries = [m.strip() for m in diet_line.split(';')]
            for m in meal_entries: # Format: "breakfast 8 am"
                parts = m.split()
                meal_name = parts[0].lower()
                meal_time = " ".join(parts[1:]).strip()
                diet[meal_name] = convert_time_to_24h(meal_time)
        else: # Drug line
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                drug = match.group(1).strip()
                freq_word = match.group(2).lower().strip()
                times_str = match.group(3)
                preferred_times = [t.strip() for t in times_str.split(',')] if times_str else []
                frequency = freq_map.get(freq_word, 1)
                prescriptions.append({
                    "name": drug,
                    "frequency": frequency,
                    "preferred_times": preferred_times
                })
    return prescriptions, diet

def convert_time_to_24h(time_str): # Simple conversion assuming format like "8 am", "1 pm"
    parts = time_str.split()
    hour = int(parts[0])
    ampm = parts[1].lower()
    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return f"{hour:02d}:00"