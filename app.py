import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Page Setup
st.set_page_config(
    page_title="EEE SUST - Classroom Booking System",
    page_icon="⚡",
    layout="wide"
)

# --- 1. DISPLAY UNIVERSITY & DEPARTMENT LOGOS ---
col_logo1, col_header, col_logo2 = st.columns([1, 4, 1])

with col_logo1:
    if os.path.exists("logo_sust.png"):
        st.image("logo_sust.png", width=110)
    else:
        st.write("🏫 **SUST**")

with col_header:
    st.title("Department of EEE, SUST")
    st.subheader("Classroom Routine & Smart Booking Control System")
    st.caption("Shahjalal University of Science and Technology, Sylhet")

with col_logo2:
    if os.path.exists("logo_eee.png"):
        st.image("logo_eee.png", width=110)
    else:
        st.write("⚡ **EEE**")

st.markdown("---")

# --- 2. ACADEMIC CREDENTIALS & CONSTANTS ---
USERS_DB = {
    "CR-EEE-41": {"password": "cr41password", "role": "CR", "name": "EEE-4/1 CR", "batch": "EEE-4/1"},
    "CR-EEE-42": {"password": "cr42password", "role": "CR", "name": "EEE-4/2 CR", "batch": "EEE-4/2"},
    "T-EEE-RA": {"password": "teacher123", "role": "Teacher", "name": "Dr. Refat Ahmed", "batch": "Faculty"},
    "T-EEE-SK": {"password": "teacher456", "role": "Teacher", "name": "Prof. S. Khan", "batch": "Faculty"},
    "ADMIN-EEE": {"password": "adminrootpass", "role": "Admin", "name": "Head of EEE Dept", "batch": "Admin"}
}

BATCHES = ["EEE-1/1", "EEE-1/2", "EEE-2/1", "EEE-2/2", "EEE-3/1", "EEE-3/2", "EEE-4/1", "EEE-4/2"]
CLASSROOMS = ["Room 429", "Room 431", "Room 529", "Room 531", "Room 530-Simulation Lab", "Circuit Lab", "Auditorium"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# Dynamic dates for upcoming week
def get_upcoming_week_dates():
    today = datetime.now()
    dates_dict = {}
    for i in range(7):
        d = today + timedelta(days=i)
        day_name = d.strftime("%A")
        full_str = d.strftime("%A (%b %d, %Y)")
        dates_dict[full_str] = day_name
    return dates_dict


WEEK_DATES_DICT = get_upcoming_week_dates()
WEEK_DATES_LIST = list(WEEK_DATES_DICT.keys())

# --- 3. SESSION STATE INITIALIZATION ---
if "time_slots" not in st.session_state:
    st.session_state.time_slots = [
        "08:30 AM - 09:30 AM",
        "09:30 AM - 10:30 AM",
        "10:30 AM - 11:30 AM",
        "11:30 AM - 12:30 PM",
        "01:30 PM - 02:30 PM",
        "02:30 PM - 03:30 PM",
        "03:30 PM - 04:30 PM"
    ]

# Master Weekly Routine set by Department Admin (Applies continuously every week)
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

# Temporary CR/Teacher dynamic reservations
if "ad_hoc_bookings" not in st.session_state:
    st.session_state.ad_hoc_bookings = []

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None


# Query Helper: Combines Master Routine + Temporary Bookings
def get_slot_status(dateday_str, slot, room):
    day_name = WEEK_DATES_DICT[dateday_str]

    # 1. Check temporary bookings for exact date
    for b in st.session_state.ad_hoc_bookings:
        if b["DateDay"] == dateday_str and b["Slot"] == slot and b["Classroom"] == room:
            return b

    # 2. Check recurring Master Semester Routine for weekday name
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


# --- 4. SECURE SIDEBAR LOGINS ---
st.sidebar.title("🔐 EEE Portal Login")

if st.session_state.logged_user is None:
    st.sidebar.subheader("User Login")
    input_uid = st.sidebar.text_input("Unique ID", placeholder="e.g. CR-EEE-41, ADMIN-EEE").strip()
    input_pwd = st.sidebar.text_input("Password", type="password").strip()

    if st.sidebar.button("Login", type="primary", use_container_width=True):
        if input_uid in USERS_DB and USERS_DB[input_uid]["password"] == input_pwd:
            st.session_state.logged_user = {
                "uid": input_uid,
                "role": USERS_DB[input_uid]["role"],
                "name": USERS_DB[input_uid]["name"],
                "batch": USERS_DB[input_uid]["batch"]
            }
            st.sidebar.success(f"Welcome, {USERS_DB[input_uid]['name']}!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials!")
else:
    user = st.session_state.logged_user
    st.sidebar.success("🟢 **Logged In**")
    st.sidebar.markdown(f"**User:** {user['name']}\n\n**Role:** `{user['role']}`\n\n**ID:** `{user['uid']}`")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_user = None
        st.rerun()

# --- 5. MAIN INTERFACE & TAB NAVIGATION ---
logged_role = st.session_state.logged_user["role"] if st.session_state.logged_user else None

if logged_role == "Teacher":
    tab_teacher, tab1, tab2, tab3 = st.tabs(
        ["👨‍🏫 My Classes Today", "📅 Availability Matrix", "➕ Reserve Extra Slot", "🔄 Free/Cancel Slot"])
elif logged_role == "Admin":
    tab1, tab2, tab3, tab_admin = st.tabs(
        ["📅 Availability Matrix", "➕ Reserve Extra Slot", "🔄 Free/Cancel Slot", "⚙️ Admin Master Routine"])
    tab_teacher = None
else:
    tab1, tab2, tab3 = st.tabs(["📅 Availability Matrix", "➕ Reserve Extra Slot", "🔄 Free/Cancel Slot"])
    tab_teacher = None

# --- TEACHER TAB ---
if tab_teacher and logged_role == "Teacher":
    with tab_teacher:
        teacher_name = st.session_state.logged_user["name"]
        st.subheader(f"👨‍🏫 Assigned Schedule for {teacher_name}")
        t_selected_date = st.selectbox("Select Date", WEEK_DATES_LIST, key="t_date")

        my_classes = []
        for slot in st.session_state.time_slots:
            for room in CLASSROOMS:
                status = get_slot_status(t_selected_date, slot, room)
                if status and status["Teacher"].lower() == teacher_name.lower():
                    my_classes.append(status)

        if my_classes:
            st.markdown(f"#### Scheduled classes for **{t_selected_date}**:")
            for c in my_classes:
                st.info(f"⏰ **{c['Slot']}** | 🏫 **{c['Classroom']}** | 🎓 **Batch:** {c['Batch']} | Type: `{c['Type']}`")
        else:
            st.success("🎉 No classes scheduled for you on this day.")

# --- TAB 1: AVAILABILITY & DYNAMIC BATCH FILTERING ---
with tab1:
    st.subheader("📅 Classroom Routine & Availability Tracker")

    col_d, col_f = st.columns(2)
    with col_d:
        selected_date = st.selectbox("Select Date & Day", WEEK_DATES_LIST)
    with col_f:
        filter_batch = st.selectbox("🔍 Filter Schedule by Batch:", ["All Batches"] + BATCHES)

    st.markdown("---")

    # AUTO-SWITCH TO FULL BATCH MODE WHEN A SPECIFIC BATCH IS SELECTED
    if filter_batch != "All Batches":
        st.markdown(f"### 🎓 Full Daily Schedule for **{filter_batch}** ({selected_date})")
        st.caption("Showing all reserved classes across all classrooms and time slots.")

        batch_classes_found = []

        for slot in st.session_state.time_slots:
            for room in CLASSROOMS:
                booking = get_slot_status(selected_date, slot, room)
                if booking and booking["Batch"] == filter_batch:
                    batch_classes_found.append(booking)

        if batch_classes_found:
            for c in batch_classes_found:
                st.info(
                    f"⏰ **{c['Slot']}** | 🏫 **{c['Classroom']}** | "
                    f"👨‍🏫 **Teacher:** {c['Teacher']} | `{c.get('Type', 'Ad-hoc Booking')}`"
                )
        else:
            st.success(f"🎉 No scheduled classes found for {filter_batch} on {selected_date}.")

    # SINGLE ROOM / MANUAL FILTERING MODE (WHEN ALL BATCHES IS SELECTED)
    else:
        col_r, col_s = st.columns(2)
        with col_r:
            selected_room = st.selectbox("Select Classroom", ["All Rooms"] + CLASSROOMS)
        with col_s:
            selected_slot_filter = st.selectbox("Select Time Slot", ["All Slots"] + st.session_state.time_slots)

        st.markdown(f"### 🏫 Room View: **{selected_room}** | **{selected_slot_filter}** ({selected_date})")

        target_rooms = CLASSROOMS if selected_room == "All Rooms" else [selected_room]
        target_slots = st.session_state.time_slots if selected_slot_filter == "All Slots" else [selected_slot_filter]

        for room in target_rooms:
            st.markdown(f"#### 📍 {room}")
            for slot in target_slots:
                booking = get_slot_status(selected_date, slot, room)
                if booking:
                    b_type = booking.get("Type", "Ad-hoc Booking")
                    st.error(
                        f"🔴 **{slot}** | **Batch:** {booking['Batch']} | "
                        f"**Teacher:** {booking['Teacher']} (`{b_type}`)"
                    )
                else:
                    st.success(f"🟢 **{slot}** | **Status:** Free / Open for Booking")

# --- TAB 2: AD-HOC RESERVATIONS ---
with tab2:
    st.subheader("Reserve an Open Slot")
    if st.session_state.logged_user is None:
        st.warning("🔒 Please login from the sidebar using your Unique ID and Password.")
    else:
        current_user = st.session_state.logged_user

        with st.form("booking_form", clear_on_submit=True):
            st.info(f"Booking as: **{current_user['name']}** (`{current_user['role']}`)")

            b_date = st.selectbox("Date & Day", WEEK_DATES_LIST)
            b_slot = st.selectbox("Time Slot", st.session_state.time_slots)
            b_room = st.selectbox("Classroom", CLASSROOMS)

            if current_user["role"] == "CR":
                target_batch = st.text_input("Target Batch", value=current_user["batch"], disabled=True)
            else:
                target_batch = st.selectbox("Target Batch", BATCHES)

            if current_user["role"] == "Teacher":
                assigned_teacher = st.text_input("Conducting Teacher", value=current_user["name"], disabled=True)
            else:
                assigned_teacher = st.text_input("Conducting Teacher Name", placeholder="e.g. Dr. Refat Ahmed")

            submit_btn = st.form_submit_button("Confirm Reservation", use_container_width=True)

            if submit_btn:
                existing = get_slot_status(b_date, b_slot, b_room)
                if existing:
                    st.error(f"❌ Slot occupied by **{existing['Batch']}** ({existing['Teacher']}).")
                else:
                    st.session_state.ad_hoc_bookings.append({
                        "DateDay": b_date,
                        "Slot": b_slot,
                        "Classroom": b_room,
                        "Batch": target_batch,
                        "BookedBy": current_user["uid"],
                        "Role": current_user["role"],
                        "Teacher": assigned_teacher,
                        "Type": "CR/Teacher Reserve"
                    })
                    st.success("✅ Slot reserved successfully!")
                    st.rerun()

# --- TAB 3: CANCELLATIONS ---
with tab3:
    st.subheader("Free Up / Cancel a Booking")
    if st.session_state.logged_user is None:
        st.warning("🔒 Please login to manage or cancel slots.")
    else:
        if st.session_state.ad_hoc_bookings:
            opts = [f"{b['DateDay']} | {b['Slot']} | {b['Classroom']} | Batch: {b['Batch']}" for b in
                    st.session_state.ad_hoc_bookings]
            selected_cancel = st.selectbox("Select Extra Booking to Free", opts)

            if st.button("Cancel Selected Booking", type="primary", use_container_width=True):
                idx = opts.index(selected_cancel)
                st.session_state.ad_hoc_bookings.pop(idx)
                st.success("🔓 Reserved slot freed successfully!")
                st.rerun()
        else:
            st.info("No active extra reservations to cancel.")

# --- ADMIN TAB: EDIT MASTER SEMESTER ROUTINE ---
if logged_role == "Admin" and tab_admin:
    with tab_admin:
        st.subheader("⚙️ Department Master Routine Management")
        st.caption("Assign recurring weekly classes (Rooms, Slots, Batches, Teachers) for the full semester.")

        with st.form("admin_routine_form", clear_on_submit=True):
            st.markdown("##### Add New Recurring Class to Master Routine")
            r_day = st.selectbox("Day of Week", DAYS)
            r_slot = st.selectbox("Time Slot", st.session_state.time_slots)
            r_room = st.selectbox("Classroom", CLASSROOMS)
            r_batch = st.selectbox("Batch", BATCHES)
            r_teacher = st.text_input("Assigned Teacher Name")

            add_routine_btn = st.form_submit_button("➕ Add to Master Routine", use_container_width=True)
            if add_routine_btn:
                if not r_teacher:
                    st.error("Please specify a teacher name.")
                else:
                    st.session_state.master_routine.append({
                        "Day": r_day,
                        "Slot": r_slot,
                        "Classroom": r_room,
                        "Batch": r_batch,
                        "Teacher": r_teacher,
                        "Type": "Master Routine"
                    })
                    st.success(f"Added recurring class for {r_batch} on {r_day}s!")
                    st.rerun()

        st.markdown("---")
        st.markdown("##### Current Master Semester Routine")
        if st.session_state.master_routine:
            df_m = pd.DataFrame(st.session_state.master_routine)
            st.dataframe(df_m, use_container_width=True)

            if st.button("⚠️ Clear Entire Master Routine", type="primary"):
                st.session_state.master_routine = []
                st.success("Master routine cleared!")
                st.rerun()

# --- 6. MASTER DATA VIEW ---
st.markdown("---")
with st.expander("📋 View Master Semester Schedule Data"):
    if st.session_state.master_routine:
        st.dataframe(pd.DataFrame(st.session_state.master_routine), use_container_width=True)
