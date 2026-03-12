import csv
import time
import requests

EDGE_URL = "http://localhost:5000/send_data"
CSV_FILE = "sensors/dataset.csv"

def send_sensor_data():

    with open(CSV_FILE, newline='') as file:
        reader = csv.DictReader(file)

        for row in reader:

            data = {
                "patient_id": row["patient_id"],
                "heart_rate": int(row["heart_rate"]),
                "spo2": int(row["spo2"]),
                "timestamp": row["timestamp"]
            }

            try:
                response = requests.post(EDGE_URL, json=data)
                print("Sent:", data)
                print("Response:", response.json())

            except Exception as e:
                print("Error sending data:", e)

            time.sleep(1)   # simulate sensor interval


if __name__ == "__main__":
    print("Starting sensor emulator...")
    send_sensor_data()
    
