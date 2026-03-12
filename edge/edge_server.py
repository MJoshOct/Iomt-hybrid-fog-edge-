# edge/edge_server.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL of the fog node (Docker container port 5001)
FOG_URL = "http://localhost:5001/process_data"

@app.route('/send_data', methods=['POST'])
def receive_data():
    data = request.get_json()

    # Validate required fields
    if not data or 'patient_id' not in data or 'heart_rate' not in data or 'spo2' not in data:
        return jsonify({"error": "Invalid data"}), 400

    # Forward the data to fog node
    try:
        resp = requests.post(FOG_URL, json=data)
        return jsonify({"status": "Data forwarded to fog", "fog_response": resp.json()}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Edge server running on port 5000...")
    app.run(host='0.0.0.0', port=5000)
