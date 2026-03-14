import json

def calculate_lap_time(base_time, compound, tire_age, temp, guesses):
    speed_bonus = guesses[compound]["speed_bonus"]
    deg_rate = guesses[compound]["degradation_rate"]
    grace_period = guesses[compound]["grace_period"]
    temp_divisor = guesses["TEMP_DIVISOR"]
    
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
    
    # We start exactly where your random robot left off
    best_guesses = {
        "SOFT":   {"speed_bonus": -1.252, "degradation_rate": 0.272, "grace_period": 4},
        "MEDIUM": {"speed_bonus": -0.009, "degradation_rate": 0.151, "grace_period": 15},
        "HARD":   {"speed_bonus":  0.172, "degradation_rate": 0.046, "grace_period": 12},
        "TEMP_DIVISOR": 24.4
    }
    
    best_score = get_score(best_guesses, test_batch)
    print(f"Starting Score: {best_score}\n")
    
    # How big of a nudge to make on each attempt
    step_sizes = {
        "speed_bonus": 0.05,
        "degradation_rate": 0.01,
        "grace_period": 1,
        "TEMP_DIVISOR": 0.5
    }
    
    while True:
        improved = False
        
        # Test adjusting each tire parameter up and down
        for compound in ["SOFT", "MEDIUM", "HARD"]:
            for param in ["speed_bonus", "degradation_rate", "grace_period"]:
                original_value = best_guesses[compound][param]
                step = step_sizes[param]
                
                # Test UP
                best_guesses[compound][param] = original_value + step
                up_score = get_score(best_guesses, test_batch)
                
                # Test DOWN
                best_guesses[compound][param] = original_value - step
                down_score = get_score(best_guesses, test_batch)
                
                # Keep whichever direction was best
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
                    best_guesses[compound][param] = original_value # Undo if neither helped
        
        # Test adjusting Temperature Divisor
        orig_temp = best_guesses["TEMP_DIVISOR"]
        
        best_guesses["TEMP_DIVISOR"] = orig_temp + step_sizes["TEMP_DIVISOR"]
        up_score = get_score(best_guesses, test_batch)
        
        best_guesses["TEMP_DIVISOR"] = orig_temp - step_sizes["TEMP_DIVISOR"]
        down_score = get_score(best_guesses, test_batch)
        
        if up_score < best_score and up_score <= down_score:
            best_score = up_score
            best_guesses["TEMP_DIVISOR"] = orig_temp + step_sizes["TEMP_DIVISOR"]
            improved = True
            print(f"Score dropped to {best_score}! (TEMP_DIVISOR -> {best_guesses['TEMP_DIVISOR']:.3f})")
        elif down_score < best_score and down_score < up_score:
            best_score = down_score
            improved = True
            print(f"Score dropped to {best_score}! (TEMP_DIVISOR -> {best_guesses['TEMP_DIVISOR']:.3f})")
        else:
            best_guesses["TEMP_DIVISOR"] = orig_temp
            
        # If the robot tested every parameter and NOTHING improved the score, it zooms in!
        if not improved:
            print("\n🔍 Hit a wall! Shrinking step sizes to zoom in closer...")
            step_sizes["speed_bonus"] *= 0.5
            step_sizes["degradation_rate"] *= 0.5
            step_sizes["TEMP_DIVISOR"] *= 0.5
            
            # Once the adjustments get microscopically small, we stop!
            if step_sizes["speed_bonus"] < 0.001:
                print("\n🏆 OPTIMIZATION COMPLETE! Final perfect guesses:")
                print(json.dumps(best_guesses, indent=2))
                break

if __name__ == "__main__":
    run_hill_climber()