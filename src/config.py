# src/config.py

USERS_DB = {
    "CR-EEE-41": {"password": "cr41password", "role": "CR", "name": "EEE-4/1 CR", "batch": "EEE-4/1"},
    "CR-EEE-42": {"password": "cr42password", "role": "CR", "name": "EEE-4/2 CR", "batch": "EEE-4/2"},
    "T-EEE-RA": {"password": "teacher123", "role": "Teacher", "name": "Dr. Refat Ahmed", "batch": "Faculty"},
    "T-EEE-SK": {"password": "teacher456", "role": "Teacher", "name": "Prof. S. Khan", "batch": "Faculty"},
    "ADMIN-EEE": {"password": "adminrootpass", "role": "Admin", "name": "Head of EEE Dept", "batch": "Admin"}
}

BATCHES = ["EEE-1/1", "EEE-1/2", "EEE-2/1", "EEE-2/2", "EEE-3/1", "EEE-3/2", "EEE-4/1", "EEE-4/2"]

CLASSROOMS = [
    "Room 429", 
    "Room 431", 
    "Room 529", 
    "Room 531", 
    "Room 530-Simulation Lab", 
    "Circuit Lab", 
    "Machine Lab", 
    "Exam Center-1029"
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

DEFAULT_TIME_SLOTS = [
    "08:30 AM - 09:30 AM",
    "09:30 AM - 10:30 AM",
    "10:30 AM - 11:30 AM",
    "11:30 AM - 12:30 PM",
    "01:30 PM - 02:30 PM",
    "02:30 PM - 03:30 PM",
    "03:30 PM - 04:30 PM"
]
