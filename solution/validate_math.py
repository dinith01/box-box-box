import json
from race_simulator import simulate_race

def test_my_guesses():
    # Load the first batch of historical races
    with open('data/historical_races/races_00000-00999.json', 'r') as f:
        races = json.load(f)
    
    # Let's just test the very first race in the file
    first_race = races[0]
    
    print(f"Testing Race: {first_race['race_id']}")
    print(f"Track: {first_race['race_config']['track']} | Temp: {first_race['race_config']['track_temp']}C")
    
    # Run the race through your simulator
    my_prediction = simulate_race(first_race)
    my_order = my_prediction["finishing_positions"]
    
    # Grab the actual historical results
    actual_order = first_race["finishing_positions"]
    
    # Compare them!
    correct_positions = 0
    for i in range(20):
        if my_order[i] == actual_order[i]:
            correct_positions += 1
            
    print(f"Accuracy: {correct_positions} out of 20 positions correct.")
    
    if correct_positions == 20:
        print("🏆 YOUR MATH IS PERFECT FOR THIS RACE!")
    else:
        print("❌ Math is incorrect. Keep tweaking!")
        print(f"Actual Winner: {actual_order[0]} | Your Winner: {my_order[0]}")

if __name__ == "__main__":
    test_my_guesses()