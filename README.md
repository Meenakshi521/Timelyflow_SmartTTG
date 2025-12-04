# Timelyflow_SmartTTG
A powerful and modern Streamlit-based timetable generator that allows institutions to manage, generate, and edit academic schedules with ease. TimelyFlow supports automated timetable generation, manual entries, dataset uploads, resource management, and secure deletion confirmations—all wrapped in a beautiful animated UI.

🚀 Features

✅ 1. Auto Timetable Generator

Generates complete timetables based on selected days, time slots, and lunch break rules.

Ensures each slot is filled with randomly assigned faculty and rooms.

Supports export to Excel.

✍️ 2. Manual Timetable Entry

Add custom rows manually (Day, Slot, Subject, Faculty, Room).

Edits are stored locally using JSON + Excel export.

📁 3. Resource Management

Manage essential academic resources:

✨ Faculties (Faculty – Subject mapping)

🏫 Rooms (Room No – Capacity)

Includes:

Add, delete, and full delete with confirmation dialogs.

Auto syncs changes to JSON files.

📤 4. Upload Timetables / Datasets

Upload external timetables or datasets via:

CSV

Excel (.xlsx)

Preview uploaded data and delete when needed.

🔐 5. Smart Confirmation Dialog System

Uses a custom Streamlit st.dialog() component to prevent accidental data loss.
Every delete action triggers a confirmation popup.

🎨 6. Modern Glassmorphism UI

Animated gradient background

Smooth shadows and glowing titles

Responsive layout with styled cards and buttons

🛠 Built With

Python 3

Streamlit

Pandas

OpenPyXL

JSON storage system

📂 Project Structure

TimelyFlow/

│── data/

│    ├── faculties.json

│    ├── rooms.json

│    ├── generated_timetable.json

│    ├── manual_entries.json

│    ├── uploaded_timetable.json

│    ├── dataset.json

│    ├── generated_timetable.xlsx

│    ├── manual_timetable.xlsx

│── app.py  ← Main Streamlit Application

│── README.md


🧩 How It Works

1️⃣ Add Resources

Add faculty & subjects or room details.

2️⃣ Choose Auto / Manual Mode

Auto Mode → Generate timetable automatically

Manual Mode → Create a custom timetable manually

3️⃣ Save / Export

Timetables are saved automatically and exported as .xlsx.

▶️ Run Locally
pip install streamlit pandas openpyxl
streamlit run app.py

🔮 Future Improvements

-->Clash-free smart allocation (AI-based scheduling)

-->Faculty/room availability constraints

-->Multi-section timetable generation

-->Admin login system

-->Dark/light theme toggle

