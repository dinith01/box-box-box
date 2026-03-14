import sys
import json

# Your brand new, highly accurate numbers!
TIRE_MATH_GUESSES = {
    "SOFT":   {"speed_bonus": -1.236, "degradation_rate": 0.258, "grace_period": 3},
    "MEDIUM": {"speed_bonus": -0.062, "degradation_rate": 0.145, "grace_period": 14},
    "HARD":   {"speed_bonus":  0.161, "degradation_rate": 0.059, "grace_period": 14},
    "TEMP_DIVISOR": 25.7
}

def calculate_lap_time(base_time, tire_compound, tire_age, track_temp):
    speed_bonus = TIRE_MATH_GUESSES[tire_compound]["speed_bonus"]
    deg_rate = TIRE_MATH_GUESSES[tire_compound]["degradation_rate"]
    grace_period = TIRE_MATH_GUESSES[tire_compound]["grace_period"]
    temp_divisor = TIRE_MATH_GUESSES["TEMP_DIVISOR"]
    
    # NEW RULE: Tires only degrade AFTER the grace period is over!
    effective_age = max(0, tire_age - grace_period)
    
    # Calculate penalty
    temp_modifier = track_temp / temp_divisor
    time_lost_to_wear = effective_age * deg_rate * temp_modifier
    
    return base_time + speed_bonus + time_lost_to_wear

def simulate_race(input_data):
    config = input_data["race_config"]
    strategies = input_data["strategies"]
    results = []

    for pos, strategy in strategies.items():
        driver_id = strategy["driver_id"]
        current_tire = strategy["starting_tire"]
        
        # Convert pit stops into a dictionary so we can easily look up the lap
        pit_stops = {stop["lap"]: stop for stop in strategy["pit_stops"]}
            
        total_time = 0.0
        tire_age = 0
        
        for lap in range(1, config["total_laps"] + 1):
            tire_age += 1 # Tires get 1 lap older
            
            # Use the Smart Math!
            total_time += calculate_lap_time(
                config["base_lap_time"], 
                current_tire, 
                tire_age, 
                config["track_temp"]
            )
            
            # Handle pit stops
            if lap in pit_stops:
                total_time += config["pit_lane_time"]
                current_tire = pit_stops[lap]["to_tire"] # Put on new shoes
                tire_age = 0 # Reset tire age to fresh
                
        results.append({"driver_id": driver_id, "total_time": total_time})

    results.sort(key=lambda x: x["total_time"])
    
    output = {
        "race_id": input_data["race_id"],
        "finishing_positions": [r["driver_id"] for r in results]
    }
    return output

if __name__ == "__main__":
    input_data = json.loads(sys.stdin.read())
    print(json.dumps(simulate_race(input_data)))