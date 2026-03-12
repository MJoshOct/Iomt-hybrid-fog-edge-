FROM python:3.11-slim

WORKDIR /app

COPY fog_node.py .
COPY patient_data.db .

# Install necessary Python packages
RUN pip install flask paho-mqtt requests

EXPOSE 5001

# Run the fog node
CMD ["python", "fog_node.py"]
