import json

def calculate_lap_time(base_time, compound, tire_age, temp, guesses):
    speed_bonus = guesses[compound]["speed_bonus"]
    deg_rate = guesses[compound]["degradation_rate"]
    grace_period = guesses[compound]["grace_period"]
    
    base_temp = guesses["BASE_TEMP"]
    temp_weight = guesses["TEMP_WEIGHT"]
    
    effective_age = max(0, tire_age - grace_period)
    
    # THE GAME DEVELOPER TEMPERATURE FORMULA
    temp_modifier = 1.0 + (temp - base_temp) * temp_weight
    
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

def get_score(guesses, test_batch):
    total_error = 0
    for race in test_batch:
        my_order = simulate_test_race(race, guesses)
        actual_order = race["finishing_positions"]
        for driver in actual_order:
            my_pos = my_order.index(driver)
            actual_pos = actual_order.index(driver)
            total_error += abs(my_pos - actual_pos)
    return total_error

def run_hill_climber():
    print("Loading historical races...")
    with open('data/historical_races/races_00000-00999.json', 'r') as f:
        all_races = json.load(f)
        
    test_batch = all_races[0:250] 
    
    # We start with CLEAN numbers based on your last successful run
    best_guesses = {
        "SOFT":   {"speed_bonus": -1.40, "degradation_rate": 0.30, "grace_period": 4},
        "MEDIUM": {"speed_bonus": 0.0,   "degradation_rate": 0.15, "grace_period": 15},
        "HARD":   {"speed_bonus": 0.20,  "degradation_rate": 0.05, "grace_period": 12},
        "BASE_TEMP": 25.0,
        "TEMP_WEIGHT": 0.01
    }
    
    best_score = get_score(best_guesses, test_batch)
    print(f"Starting Score: {best_score}\n")
    
    step_sizes = {
        "speed_bonus": 0.05,
        "degradation_rate": 0.01,
        "grace_period": 1,
        "BASE_TEMP": 1.0,
        "TEMP_WEIGHT": 0.005
    }
    
    while True:
        improved = False
        
        # Test tire numbers
        for compound in ["SOFT", "MEDIUM", "HARD"]:
            for param in ["speed_bonus", "degradation_rate", "grace_period"]:
                original_value = best_guesses[compound][param]
                step = step_sizes[param]
                
                best_guesses[compound][param] = original_value + step
                up_score = get_score(best_guesses, test_batch)
                
                best_guesses[compound][param] = original_value - step
                down_score = get_score(best_guesses, test_batch)
                
                if up_score < best_score and up_score <= down_score:
                    best_score = up_score
                    best_guesses[compound][param] = original_value + step
                    improved = True
                    print(f"Score dropped to {best_score}! ({compound} {param} -> {best_guesses[compound][param]:.3f})")
                elif down_score < best_score and down_score < up_score:
                    best_score = down_score
                    improved = True
                    print(f"Score dropped to {best_score}! ({compound} {param} -> {best_guesses[compound][param]:.3f})")
                else:
                    best_guesses[compound][param] = original_value
        
        # Test global temperature numbers
        for param in ["BASE_TEMP", "TEMP_WEIGHT"]:
            original_value = best_guesses[param]
            step = step_sizes[param]
            
            best_guesses[param] = original_value + step
            up_score = get_score(best_guesses, test_batch)
            
            best_guesses[param] = original_value - step
            down_score = get_score(best_guesses, test_batch)
            
            if up_score < best_score and up_score <= down_score:
                best_score = up_score
                best_guesses[param] = original_value + step
                improved = True
                print(f"Score dropped to {best_score}! ({param} -> {best_guesses[param]:.3f})")
            elif down_score < best_score and down_score < up_score:
                best_score = down_score
                improved = True
                print(f"Score dropped to {best_score}! ({param} -> {best_guesses[param]:.3f})")
            else:
                best_guesses[param] = original_value
            
        if not improved:
            print("\n🔍 Zooming in closer...")
            step_sizes["speed_bonus"] *= 0.5
            step_sizes["degradation_rate"] *= 0.5
            step_sizes["TEMP_WEIGHT"] *= 0.5
            
            # Stop when we hit a highly refined number
            if step_sizes["speed_bonus"] < 0.005:
                print("\n🏆 OPTIMIZATION COMPLETE! Clean human numbers:")
                print(json.dumps(best_guesses, indent=2))
                break

if __name__ == "__main__":
    run_hill_climber()