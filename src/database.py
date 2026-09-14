# src/database.py
import streamlit as st
from datetime import datetime, timedelta
from src.config import DEFAULT_TIME_SLOTS

def get_upcoming_week_dates():
    today = datetime.now()
    dates_dict = {}
    for i in range(7):
        d = today + timedelta(days=i)
        day_name = d.strftime("%A")
        full_str = d.strftime("%A (%b %d, %Y)")
        dates_dict[full_str] = day_name
    return dates_dict

def init_session_state():
    if "time_slots" not in st.session_state:
        st.session_state.time_slots = DEFAULT_TIME_SLOTS

    if "master_routine" not in st.session_state:
        st.session_state.master_routine = [
            {
                "Day": "Monday",
                "Slot": "08:30 AM - 09:30 AM",
                "Classroom": "Room 429",
                "Batch": "EEE-4/1",
                "Teacher": "Dr. Refat Ahmed",
                "Type": "Master Routine"
            },
            {
                "Day": "Wednesday",
                "Slot": "10:30 AM - 11:30 AM",
                "Classroom": "Room 530-Simulation Lab",
                "Batch": "EEE-4/2",
                "Teacher": "Prof. S. Khan",
                "Type": "Master Routine"
            }
        ]

    if "ad_hoc_bookings" not in st.session_state:
        st.session_state.ad_hoc_bookings = []

    if "logged_user" not in st.session_state:
        st.session_state.logged_user = None

def get_slot_status(dateday_str, slot, room, week_dates_dict):
    day_name = week_dates_dict[dateday_str]
    
    for b in st.session_state.ad_hoc_bookings:
        if b["DateDay"] == dateday_str and b["Slot"] == slot and b["Classroom"] == room:
            return b
            
    for m in st.session_state.master_routine:
        if m["Day"] == day_name and m["Slot"] == slot and m["Classroom"] == room:
            return {
                "DateDay": dateday_str,
                "Slot": slot,
                "Classroom": room,
                "Batch": m["Batch"],
                "Teacher": m["Teacher"],
                "BookedBy": "Dept Routine",
                "Type": "Master Routine"
            }
    return None
