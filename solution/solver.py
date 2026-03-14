import json
import random

def calculate_lap_time(base_time, compound, tire_age, temp, guesses):
    speed_bonus = guesses[compound]["speed_bonus"]
    deg_rate = guesses[compound]["degradation_rate"]
    grace_period = guesses[compound]["grace_period"]
    temp_divisor = guesses["TEMP_DIVISOR"]
    
    # NEW RULE: Tires don't degrade if they are within their grace period!
    # If age is 3, and grace is 5, effective_age is 0. 
    effective_age = max(0, tire_age - grace_period)
    
    temp_modifier = temp / temp_divisor
    time_lost_to_wear = effective_age * deg_rate * temp_modifier
    
    return base_time + speed_bonus + time_lost_to_wear

def simulate_test_race(race_data, guesses):
    config = race_data["race_config"]
    strategies = race_data["strategies"]
    results = []

    for pos, strategy in strategies.items():
        driver_id = strategy["driver_id"]
        current_tire = strategy["starting_tire"]
        pit_stops = {stop["lap"]: stop for stop in strategy["pit_stops"]}
            
        total_time = 0.0
        tire_age = 0
        
        for lap in range(1, config["total_laps"] + 1):
            tire_age += 1
            total_time += calculate_lap_time(
                config["base_lap_time"], current_tire, tire_age, config["track_temp"], guesses
            )
            
            if lap in pit_stops:
                total_time += config["pit_lane_time"]
                current_tire = pit_stops[lap]["to_tire"]
                tire_age = 0
                
        results.append({"driver_id": driver_id, "total_time": total_time})

    results.sort(key=lambda x: x["total_time"])
    return [r["driver_id"] for r in results]

def run_robot_solver():
    print("Loading historical races...")
    with open('data/historical_races/races_00000-00999.json', 'r') as f:
        all_races = json.load(f)
        
    # Test against 10 races to be extra sure!
    test_batch = all_races[0:10] 
    
    best_score = 999999 

    print("Starting the Ultimate Robot! Press Ctrl+C when the score hits 0.\n")
    
    attempts = 0
    while True:
        attempts += 1
        
        # We give the robot wide bounds to find the new grace periods
        test_guesses = {
            "SOFT": {
                "speed_bonus": round(random.uniform(-1.40, -1.20), 3),
                "degradation_rate": round(random.uniform(0.23, 0.27), 3),
                "grace_period": random.randint(1, 3) 
            },
            "MEDIUM": {
                "speed_bonus": round(random.uniform(-0.25, -0.05), 3),
                "degradation_rate": round(random.uniform(0.11, 0.15), 3),
                "grace_period": random.randint(10, 14) 
            },
            "HARD": {
                "speed_bonus": round(random.uniform(0.05, 0.20), 3),
                "degradation_rate": round(random.uniform(0.05, 0.09), 3),
                "grace_period": random.randint(13, 17) 
            },
            # Your last run found 26.6, so we search around there!
            "TEMP_DIVISOR": round(random.uniform(25.0, 28.0), 1)
        }
        
        total_error = 0
        for race in test_batch:
            my_order = simulate_test_race(race, test_guesses)
            actual_order = race["finishing_positions"]
            
            for driver in actual_order:
                my_pos = my_order.index(driver)
                actual_pos = actual_order.index(driver)
                total_error += abs(my_pos - actual_pos)
                
        if total_error < best_score:
            best_score = total_error
            print(f"--- NEW BEST SCORE: {best_score} (Attempt #{attempts}) ---")
            print(json.dumps(test_guesses, indent=2))
            
            if best_score == 0:
                print("\n🏆 PERFECT MATCH FOUND!")
                break

if __name__ == "__main__":
    run_robot_solver()