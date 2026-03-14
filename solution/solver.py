import json
import random

# We import your simulator so the robot can use it!
import race_simulator 

def calculate_error_score(guesses, races_to_test):
    # 1. Plug the robot's new guesses into your simulator
    race_simulator.TIRE_MATH_GUESSES = guesses
    
    total_error_distance = 0
    
    # 2. Run a few test races
    for race in races_to_test:
        prediction = race_simulator.simulate_race(race)
        my_order = prediction["finishing_positions"]
        actual_order = race["finishing_positions"]
        
        # 3. Calculate how "wrong" the order is.
        # If a driver finished 1st, but we predicted 5th, that is an error of 4.
        # We want the total error to be 0!
        for driver in actual_order:
            my_pos = my_order.index(driver)
            actual_pos = actual_order.index(driver)
            total_error_distance += abs(my_pos - actual_pos)
            
    return total_error_distance

def run_robot_solver():
    print("Loading historical races...")
    with open('data/historical_races/races_00000-00999.json', 'r') as f:
        all_races = json.load(f)
        
    # Let's just test against the first 5 races to keep it fast
    test_batch = all_races[0:5] 
    
    # Start with a terrible score so the robot can easily beat it
    best_score = 999999 
    best_guesses = {}

    print("Starting the robot! Press Ctrl+C to stop it when you are happy.\n")
    
    attempts = 0
    while True:
        attempts += 1
        
        # The robot randomly generates new rules to test
        # We give it logical bounds (Soft is fastest/wears fastest, Hard is slowest/wears slowest)
        test_guesses = {
            "SOFT": {
                "speed_bonus": round(random.uniform(-1.15, -0.95), 3),
                "degradation_rate": round(random.uniform(0.15, 0.21), 3)
            },
            "MEDIUM": {
                "speed_bonus": round(random.uniform(-0.40, -0.20), 3),
                "degradation_rate": round(random.uniform(0.05, 0.09), 3)
            },
            "HARD": {
                "speed_bonus": round(random.uniform(0.15, 0.35), 3),
                "degradation_rate": round(random.uniform(0.01, 0.05), 3)
            },

            "TEMP_DIVISOR": round(random.uniform(20.0, 40.0), 1)

        }
        
        # Grade the robot's guesses
        current_score = calculate_error_score(test_guesses, test_batch)
        
        # If the score is closer to 0, it's a new record!
        if current_score < best_score:
            best_score = current_score
            best_guesses = test_guesses
            print(f"--- NEW BEST SCORE: {best_score} (Attempt #{attempts}) ---")
            print(json.dumps(best_guesses, indent=2))
            
            # If the score hits 0, the math is perfect for these 5 races!
            if best_score == 0:
                print("\n🏆 PERFECT MATCH FOUND!")
                break

if __name__ == "__main__":
    run_robot_solver()