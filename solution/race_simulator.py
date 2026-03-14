import sys
import json

def simulate_race(input_data):
    # 1. Get the track details (The "Track Rules")
    config = input_data["race_config"]
    total_laps = config["total_laps"]
    base_time = config["base_lap_time"]
    pit_time = config["pit_lane_time"]
    
    # 2. Get the drivers and their strategies
    strategies = input_data["strategies"]
    
    results = [] # To store how fast each driver finishes

    # 3. Simulate the race for each driver, one by one
    for pos, strategy in strategies.items():
        driver_id = strategy["driver_id"]
        
        # We make a simple list of laps where this driver plans to stop
        pit_stop_laps = []
        for stop in strategy["pit_stops"]:
            pit_stop_laps.append(stop["lap"])
            
        total_time = 0.0
        
        # 4. Run the laps!
        for lap in range(1, total_laps + 1):
            # Every lap takes the base lap time
            total_time += base_time
            
            # If the driver stops this lap, add the pit stop time penalty
            if lap in pit_stop_laps:
                total_time += pit_time
                
        # 5. Save the driver's final time
        results.append({
            "driver_id": driver_id,
            "total_time": total_time
        })

    # 6. Sort the results (lowest time wins!)
    results.sort(key=lambda x: x["total_time"])
    
    # Extract just the driver IDs in their winning order
    finishing_positions = []
    for r in results:
        finishing_positions.append(r["driver_id"])
        
    # 7. Package the final answer exactly as the rules require
    output = {
        "race_id": input_data["race_id"],
        "finishing_positions": finishing_positions
    }
    return output

if __name__ == "__main__":
    # Read the text file from standard input
    input_json = sys.stdin.read()
    input_data = json.loads(input_json)
    
    # Run our dumb simulator
    final_result = simulate_race(input_data)
    
    # Print the final answer to standard output
    print(json.dumps(final_result))