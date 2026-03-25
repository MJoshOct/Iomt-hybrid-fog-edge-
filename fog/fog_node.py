# fog/fog_node.py
from flask import Flask, request, jsonify
from flask_cors import CORS          # FIX 3: enable CORS for frontend access
import sqlite3
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app)                            # FIX 3: apply CORS globally

# FIX 5: use thread-local storage instead of a single shared connection
_local = threading.local()

def get_db():
    """Return a per-thread SQLite connection, creating one if needed."""
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect("patient_data.db")
        _local.conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                patient_id  TEXT,
                heart_rate  INTEGER,
                spo2        INTEGER,
                status      TEXT,
                timestamp   TEXT
            )
        """)
        _local.conn.commit()
    return _local.conn

live_data = []                       # in-memory cache for recent readings
live_data_lock = threading.Lock()   # FIX 5: guard the shared list too


@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()

    # Basic validation
    if not data or 'patient_id' not in data or 'heart_rate' not in data or 'spo2' not in data:
        return jsonify({"error": "Invalid data"}), 400

    patient_id = data['patient_id']

    # FIX 6: validate numeric types before casting
    try:
        heart_rate = int(data['heart_rate'])
        spo2       = int(data['spo2'])
    except (ValueError, TypeError):
        return jsonify({"error": "heart_rate and spo2 must be integers"}), 400

    # FIX 6: validate timestamp format if provided
    raw_ts = data.get('timestamp', '')
    if raw_ts:
        try:
            datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S")
            timestamp = raw_ts
        except ValueError:
            return jsonify({"error": "timestamp must be YYYY-MM-DD HH:MM:SS"}), 400
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # FIX 4: alert detection — added low heart rate check
    if heart_rate > 110:
        status = "High Heart Rate Alert"
    elif heart_rate < 40:                    # FIX 4: medically critical
        status = "Low Heart Rate Alert"
    elif spo2 < 92:
        status = "Low Oxygen Alert"
    else:
        status = "Normal"

    # Insert into SQLite via thread-safe connection
    db = get_db()
    db.execute(
        "INSERT INTO readings (patient_id, heart_rate, spo2, status, timestamp) "
        "VALUES (?, ?, ?, ?, ?)",
        (patient_id, heart_rate, spo2, status, timestamp)
    )
    db.commit()

    # FIX 1: update live_data so the /live endpoint actually has data
    record = {
        "patient_id": patient_id,
        "heart_rate": heart_rate,
        "spo2":       spo2,
        "status":     status,
        "timestamp":  timestamp
    }
    with live_data_lock:
        live_data.append(record)
        if len(live_data) > 50:          # keep only the latest 50 in memory
            live_data.pop(0)

    print(f"[FOG] Processed: Patient {patient_id}, HR: {heart_rate}, SpO2: {spo2} → {status}")
    return jsonify({"status": status})


@app.route('/readings', methods=['GET'])
def get_readings():
    db = get_db()
    cursor = db.execute(
        "SELECT patient_id, heart_rate, spo2, status, timestamp "
        "FROM readings ORDER BY timestamp DESC LIMIT 50"
    )
    rows = cursor.fetchall()
    result = [
        {
            "patient_id": r[0],
            "heart_rate": r[1],
            "spo2":       r[2],
            "status":     r[3],
            "timestamp":  r[4]
        }
        for r in rows
    ]
    return jsonify(result)


# FIX 2: added missing @app.route decorator so /live is actually reachable
@app.route('/live', methods=['GET'])
def get_live():
    with live_data_lock:
        return jsonify(list(live_data))


if __name__ == '__main__':
    print("Fog node running on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)
