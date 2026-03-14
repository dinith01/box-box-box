import sys
import json

# THE FINAL, CRACKED FORMULA
TIRE_MATH_GUESSES = {
    "SOFT": {
        "speed_bonus": -1.39375,
        "degradation_rate": 0.31125,
        "grace_period": 4
    },
    "MEDIUM": {
        "speed_bonus": -0.03125,
        "degradation_rate": 0.1625,
        "grace_period": 15
    },
    "HARD": {
        "speed_bonus": 0.175,
        "degradation_rate": 0.05,
        "grace_period": 12
    },
    "BASE_TEMP": 22.0,
    "TEMP_WEIGHT": 0.018125
}

def calculate_lap_time(base_time, tire_compound, tire_age, track_temp):
    speed_bonus = TIRE_MATH_GUESSES[tire_compound]["speed_bonus"]
    deg_rate = TIRE_MATH_GUESSES[tire_compound]["degradation_rate"]
    grace_period = TIRE_MATH_GUESSES[tire_compound]["grace_period"]
    
    base_temp = TIRE_MATH_GUESSES["BASE_TEMP"]
    temp_weight = TIRE_MATH_GUESSES["TEMP_WEIGHT"]
    
    # Apply the Grace Period
    effective_age = max(0, tire_age - grace_period)
    
    # THE GAME DEVELOPER TEMPERATURE FORMULA
    temp_modifier = 1.0 + (track_temp - base_temp) * temp_weight
    
    # Calculate final lap time
    time_lost_to_wear = effective_age * deg_rate * temp_modifier
    
    return base_time + speed_bonus + time_lost_to_wear

def simulate_race(input_data):
    config = input_data["race_config"]
    strategies = input_data["strategies"]
    results = []

    for pos, strategy in strategies.items():
        driver_id = strategy["driver_id"]
        current_tire = strategy["starting_tire"]
        
        # Convert pit stops into a dictionary
        pit_stops = {stop["lap"]: stop for stop in strategy["pit_stops"]}
            
        total_time = 0.0
        tire_age = 0
        
        for lap in range(1, config["total_laps"] + 1):
            tire_age += 1 
            
            total_time += calculate_lap_time(
                config["base_lap_time"], 
                current_tire, 
                tire_age, 
                config["track_temp"]
            )
            
            # Handle pit stops: add the time penalty
            if lap in pit_stops:
                total_time += config["pit_lane_time"]
                current_tire = pit_stops[lap]["to_tire"] 
                tire_age = 0 
                
        results.append({"driver_id": driver_id, "total_time": total_time})

    # Sort by lowest total time (fastest wins)
    results.sort(key=lambda x: x["total_time"])
    
    # Format the exact JSON output required
    output = {
        "race_id": input_data["race_id"],
        "finishing_positions": [r["driver_id"] for r in results]
    }
    return output

if __name__ == "__main__":
    # Accept race configuration JSON from stdin
    input_data = json.loads(sys.stdin.read())
    
    # Write finishing positions JSON to stdout
    print(json.dumps(simulate_race(input_data)))