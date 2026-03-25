# edge/edge_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)                                           # FIX 5: allow cross-origin calls

# FIX 1: use Docker service name, not localhost
FOG_URL     = "http://localhost:5001/process_data"       # change 'fog' to match docker-compose service name
MAX_RETRY   = 3                                     # FIX 3: retry attempts
RETRY_DELAY = 1                                     # seconds between retries
TIMEOUT     = 5                                     # FIX 2: fog request timeout in seconds

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024       # FIX 6: 16 KB max payload


def forward_to_fog(data: dict) -> tuple[dict, int]:
    """Forward data to fog node with retry logic."""
    last_error = None

    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = requests.post(FOG_URL, json=data, timeout=TIMEOUT)   # FIX 2: timeout

            # FIX 4: separate fog-level errors from edge-level errors
            if resp.status_code == 400:
                # Fog rejected the data — no point retrying
                return {"error": "Fog rejected data", "fog_response": resp.json()}, 422

            resp.raise_for_status()
            return {"status": "forwarded", "fog_response": resp.json()}, 200

        except requests.exceptions.ConnectionError as e:
            last_error = f"Fog unreachable (attempt {attempt}/{MAX_RETRY})"
            print(f"[EDGE] {last_error}")
        except requests.exceptions.Timeout:
            last_error = f"Fog timed out (attempt {attempt}/{MAX_RETRY})"
            print(f"[EDGE] {last_error}")
        except requests.exceptions.HTTPError as e:
            last_error = str(e)
            print(f"[EDGE] HTTP error from fog: {last_error}")
            break                                  # don't retry on unexpected HTTP errors

        if attempt < MAX_RETRY:
            time.sleep(RETRY_DELAY)

    return {"error": last_error or "Failed to reach fog"}, 502   # 502 = bad gateway


@app.route('/send_data', methods=['POST'])
def receive_data():
    data = request.get_json()

    # Validate required fields
    if not data or 'patient_id' not in data or 'heart_rate' not in data or 'spo2' not in data:
        return jsonify({"error": "Invalid data"}), 400

    print(f"[EDGE] Received from sensor: Patient {data.get('patient_id')}, "
          f"HR: {data.get('heart_rate')}, SpO2: {data.get('spo2')}")

    response, status_code = forward_to_fog(data)   # FIX 3 + 4
    return jsonify(response), status_code


# Health check endpoint — useful for Docker and monitoring
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "edge running"}), 200


if __name__ == '__main__':
    print("Edge server running on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
