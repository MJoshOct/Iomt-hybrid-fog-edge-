# Iomt-hybrid-fog-edge-
This project is a miron project in which we are trying to show that a hybrid fog-edge design allows for lower latency and scalability for IoMT implementations.

Please note:
We have not implemented hardware but simulated the sensor behaviour. Docker was setup but not implemented as its use-case was not justified for goals of this project. Thus servers were made to run in local machines only. Regardless of presence of Docker files.

Project flow:
Sensor Emulator (patient data)
        ↓
Edge Server (Data Validation)
        ↓
Fog Node (Readying to send to database with access to cloud databse)
        ↓
SQLite Database
        ↓
Frontend Dashboard (monitor at fog layer and access from database in edge layer)

Different layers in which this project is divided into-

  Edge/Server Layer:
- Receives sensor data
- Forwards to fog

  Fog Layer:
- Processes data
- Detects alerts
- Stores in DB
- Maintains live buffer

  Cloud/UI Layer:
- Live monitoring (/live)
- Historical analytics (/readings)

Contributors:

Mayank Joshua Kullu

Lalit Krishna Yadav
