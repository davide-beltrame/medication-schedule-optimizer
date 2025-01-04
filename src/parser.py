import re

def parse_prescriptions(input_str: str):
    lines = input_str.strip().split('\n')
    prescriptions = []
    diet = {}
    freq_map = {"once": 1, "twice": 2, "thrice": 3}
    allowed_times = {"morning", "afternoon", "evening"}  # Allowed preferred times
    drug_pattern = r"^(.*?):\s*(once|twice|thrice)\s+daily(?:\s*\((.*?)\))?$"
    time_pattern = r"^\d{1,2}\s*(am|pm)$"  # e.g., "8 am", "1 pm"

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue  # Ignore comment lines

        if line.lower().startswith("diet:"):
            diet_line = line[len("Diet:"):].strip()
            meal_entries = [m.strip() for m in diet_line.split(';') if m.strip()]  # Filter out empty entries
            
            for m in meal_entries:  # Format: "breakfast 8 am"
                parts = m.split()
                if len(parts) < 2:  # Validate diet format
                    print("Syntax error in diet input. Please check input.")
                    exit(1)
                
                meal_name = parts[0].lower()
                meal_time = " ".join(parts[1:]).strip()

                if not re.match(time_pattern, meal_time):  # Check for valid time
                    print(f"Invalid time format for {meal_name}: '{meal_time}'. Please check input.")
                    exit(1)

                diet[meal_name] = convert_time_to_24h(meal_time)
        
        else:  # Drug line
            match = re.match(drug_pattern, line, re.IGNORECASE)
            if not match:
                print(f"Syntax error in drug input: '{line}'. Please check input.")
                exit(1)

            drug = match.group(1).strip()
            freq_word = match.group(2).lower().strip()
            times_str = match.group(3)
            
            # Validate preferred times if present
            if times_str:
                preferred_times = [t.strip() for t in times_str.split(',')]
                for t in preferred_times:
                    if t not in allowed_times:
                        print(f"Invalid preferred time '{t}' for drug '{drug}'. Allowed values are: morning, afternoon, evening.")
                        exit(1)
            else:
                preferred_times = []

            frequency = freq_map.get(freq_word, 1)

            prescriptions.append({
                "name": drug,
                "frequency": frequency,
                "preferred_times": preferred_times
            })

    return prescriptions, diet

def convert_time_to_24h(time_str):  # Simple conversion assuming format like "8 am", "1 pm"
    parts = time_str.split()
    if len(parts) != 2 or not parts[0].isdigit() or parts[1].lower() not in {"am", "pm"}:
        print(f"Invalid time format: '{time_str}'. Please use formats like '8 am' or '1 pm'.")
        exit(1)
    
    hour = int(parts[0])
    ampm = parts[1].lower()
    if hour < 1 or hour > 12:  # Validate hour range
        print(f"Invalid hour in time: '{hour}'. Must be between 1 and 12.")
        exit(1)

    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:00"