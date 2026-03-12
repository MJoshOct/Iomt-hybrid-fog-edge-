# fog/fog_node.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect("patient_data.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    patient_id TEXT,
    heart_rate INTEGER,
    spo2 INTEGER,
    status TEXT,
    timestamp TEXT
)
""")
conn.commit()

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()

    # Basic validation checks patient_id, heart_rate, oxygen saturation level in blood spo2

    if not data or 'patient_id' not in data or 'heart_rate' not in data or 'spo2' not in data:
        return jsonify({"error": "Invalid data"}), 400

    patient_id = data['patient_id']
    heart_rate = int(data['heart_rate'])
    spo2 = int(data['spo2'])
    timestamp = data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Simple alert detection
    
    status = "Normal"
    if heart_rate > 110:
        status = "High Heart Rate Alert"
    elif spo2 < 92:
        status = "Low Oxygen Alert"

    # Insert into SQLite
    
    cursor.execute(
        "INSERT INTO readings (patient_id, heart_rate, spo2, status, timestamp) VALUES (?, ?, ?, ?, ?)",
        (patient_id, heart_rate, spo2, status, timestamp)
    )
    conn.commit()

    print(f"[FOG] Processed: Patient {patient_id}, HR: {heart_rate}, SpO2: {spo2} → {status}")
    return jsonify({"status": status})

# NEW ENDPOINT FOR FRONTEND
@app.route('/readings', methods=['GET'])
def get_readings():
    cursor.execute("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()

    result = []

    for r in rows:
        result.append({
            "patient_id": r[0],
            "heart_rate": r[1],
            "spo2": r[2],
            "status": r[3],
            "timestamp": r[4]
        })

    return jsonify(result)

if __name__ == '__main__':
    print("Fog node running on port 5001...")
    app.run(host='0.0.0.0', port=5001)
