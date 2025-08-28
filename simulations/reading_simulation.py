import requests 
import datetime 
import time
import math 
import json
import random



UPDATE_INTERVAL = 5

TEMP_MIN = 10.0  # Lowest temperature in Celsius
TEMP_MAX = 25.0  # Highest temperature in Celsius
TEMP_PEAK_HOUR = 15  # 3 PM

HUMIDITY_MIN = 40.0 # Lowest humidity percentage
HUMIDITY_MAX = 85.0 # Highest humidity percentage
HUMIDITY_PEAK_HOUR = 3 # 3 AM (inverse of temperature)

LIGHT_MIN = 0     # Lowest light level (night)
LIGHT_MAX = 100000 # Max light level (full sun)
LIGHT_PEAK_HOUR = 13 # 1 PM

SOIL_MOISTURE_BASE_DECAY_RATE = 0.05
SOIL_MOISTURE_RAIN_CHANCE = 0.02


def generate_sensor_data(greenhouse_id):
    """
    Generates a dictionary of simulated sensor data following a daily pattern.
    
    The pattern is based on the current time of day to simulate realistic cycles.
    
    Returns:
        dict: A dictionary containing simulated sensor readings.
    """
    now = datetime.datetime.now()
    hour = now.hour + now.minute / 60.0
    
    # 1. Temperature: Use a sine wave to model daily cycle, peaking at 3 PM
    # The sine wave shifts so that the peak is at TEMP_PEAK_HOUR
    temp_sin_input = (hour - TEMP_PEAK_HOUR) / 24 * 2 * math.pi
    temp_midpoint = (TEMP_MAX + TEMP_MIN) / 2
    temp_amplitude = (TEMP_MAX - TEMP_MIN) / 2
    temp_celsius = temp_midpoint + temp_amplitude * math.sin(temp_sin_input)
    temp_celsius = round(temp_celsius + random.uniform(-1.5, 1.5), 2) # Add small random noise
    
    # 2. Humidity: Inversely related to temperature, peaking in the early morning
    humidity_sin_input = (hour - HUMIDITY_PEAK_HOUR) / 24 * 2 * math.pi
    humidity_midpoint = (HUMIDITY_MAX + HUMIDITY_MIN) / 2
    humidity_amplitude = (HUMIDITY_MAX - HUMIDITY_MIN) / 2
    humidity_pct = humidity_midpoint + humidity_amplitude * math.sin(humidity_sin_input)
    humidity_pct = round(humidity_pct + random.uniform(-2.0, 2.0), 2) # Add small random noise
    
    # 3. Light (lux): Follows a similar pattern to temperature but drops to near zero at night
    light_sin_input = (hour - LIGHT_PEAK_HOUR) / 24 * 2 * math.pi
    light_pct = (math.sin(light_sin_input) + 1) / 2 # Normalize sine wave to 0-1 range
    light_lux = light_pct * LIGHT_MAX
    
    # Cap light at a minimum value at night
    if hour > 20 or hour < 6: # Between 8 PM and 6 AM
        light_lux = random.uniform(50, 200) # Low ambient light
    
    light_lux = int(light_lux + random.uniform(-500, 500)) # Add small random noise
    
    # 4. CO2: Higher at night when plants respire, lower during the day
    co2_sin_input = (hour - 3) / 24 * 2 * math.pi
    co_two = 600 + 100 * math.sin(co2_sin_input)
    co_two = int(co_two + random.uniform(-20, 20)) # Add noise
    
    # 5. Wind Speed: Less cyclical, more random but with a higher baseline during the day
    wind_base = 2.0
    if hour > 8 and hour < 18:
        wind_base = 5.0 # Higher wind during the day
    wind_speed = round(wind_base + random.uniform(-2.0, 3.0), 2)
    
    # Placeholder for soil moisture - this would need to persist state
    # We will assume a simple random value for now that decreases slightly over time
    # This value should be stored and updated in a more complex simulation
    soil_moisture_pct = round(random.uniform(20.0, 70.0), 2)
    
    # Return the data as a dictionary
    return {
        "greenhouse_id": greenhouse_id,
        "temp_celsius": temp_celsius,
        "humidity_pct": humidity_pct,
        "soil_moisture_pct": soil_moisture_pct,
        "light_lux": light_lux,
        "co_two": co_two,
        "wind_speed": wind_speed
    }
    


def send_data(data):
    API_URL = f"http://127.0.0.1:5002/api/v1/readings/{data['greenhouse_id']}"
    try:
        response = requests.post(API_URL, json = data)
        response.raise_for_status()
         
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to API: {e}")
        
        

if __name__ == "__main__":
    # Example of how to use the function
    print("Generating sensor data that changes based on the time of day...")
    try:
        while True:
            simulated_data = generate_sensor_data(1)
            send_data(simulated_data)
            print(f"Data point {datetime.datetime.now()}: {simulated_data}")
            time.sleep(UPDATE_INTERVAL) 
    
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
