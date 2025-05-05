# SmartProdGuide

SmartProdGuide is a multi-component production assistance and monitoring system designed for manufacturing environments. It replaces manual paper-based preparation with a smart scanning and LED-guided process, improving accuracy and speed on the production floor.

---

## 🚀 Features

- 🔍 **Order Scanning** at production stations using Raspberry Pi
- 💡 **LED Control** for guiding operators on what to pick
- 📊 **Dashboard Monitoring** for real-time production insights
- 🖥️ **Admin Desktop App** for managing product data
- 🔒 **Role-Based Access** for operators, team leaders, supervisors, and process engineers

---

## 🏗️ Architecture

- 6 Raspberry Pi-based stations running individual GUIs
- Central web app for data handling and LED control (via MQTT)
- Dashboard app to visualize production data (units, codes, shift info)
- Desktop app for process engineers to update and push product data

---

## 📦 Project Structure

station_gui.py - Operator GUI to scan orders and send data
desktop_app.py - Used by process engineers to update product metadata
dashboard_app/py - Real-time monitoring dashboard for supervisors
images/ - needed for app
ipaddress_password_dict.json - stores desktop app data
README.md


---

## 🧑‍💻 Roles and Access

| Role                | Access Level                         |
|---------------------|--------------------------------------|
| Operator            | GUI for scanning orders              |
| Raw Material Feeder | GUI to scan and place materials      |
| Team Leader         | Dashboard (view data, plots, stats)  |
| Supervisor          | Dashboard (view only)                |
| Process Engineer    | Desktop app (data update only)       |

---

## 🔧 Technologies Used

- Python + CustomTkinter
- Raspberry Pi (per station)
- MQTT (for LED control)
- Sockets (GUI ↔ Web App communication)
- Local Storage (per Pi)
- Central Dashboard App (Tkinter)
- sqlite database