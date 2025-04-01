import serial
import json
from tinydb import TinyDB
from datetime import datetime

# Initialize TinyDB
db = TinyDB("sensor_data.json")

# Open Serial Port (Change "COM6" to your port)
ser = serial.Serial("COM6", 115200)  # Use "/dev/ttyUSB0" for Linux

while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()
            print("Received:", line)  # Debugging output

            # Parse JSON from Serial
            data = json.loads(line)
            temperature = data["temperature"]
            humidity = data["humidity"]
            air_quality = data["air_quality"]
            light_intensity = data["light_intensity"]

            # Get Current Date & Time
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")  # e.g., 2025-03-16
            time_str = now.strftime("%H:%M:%S")  # e.g., 10:30:15

            # Fetch existing data or initialize a new date entry
            db_data = db.all()
            if len(db_data) > 0:
                records = db_data[0]  # Fetch the first record
            else:
                records = {}

            # Add new data
            if date_str not in records:
                records[date_str] = {}

            records[date_str][time_str] = {
                "temperature": temperature,
                "humidity": humidity,
                "air_quality": air_quality,
                "light_intensity": light_intensity
            }

            # Update TinyDB
            db.truncate()  # Clear previous data
            db.insert(records)  # Insert updated data

            print(f"Stored: {date_str} {time_str} → Temp={temperature}°C, Hum={humidity}%, AirQ={air_quality}, Light={light_intensity}")

    except Exception as e:
        print("Error:", e)
