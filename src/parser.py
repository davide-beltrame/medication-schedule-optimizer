import re

def parse_prescriptions(input_str: str):
    """
    Parse lines of the form:
    "Warfarin: once daily (morning)"
    "Ibuprofen: thrice daily"
    "Metformin: twice daily (morning, evening)"
    """
    lines = input_str.strip().split('\n')
    prescriptions = []
    freq_map = {"once":1, "twice":2, "thrice":3}
    pattern = r"^(.*?):\s*(once|twice|thrice)\s+daily(?:\s*\((.*?)\))?$"
    
    for line in lines:
        match = re.match(pattern, line.strip(), re.IGNORECASE)
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
    return prescriptions
