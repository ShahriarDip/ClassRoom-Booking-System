import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(
    page_title="Academic Routine & Booking System",
    page_icon="🏫",
    layout="wide"
)

# --- 1. PRE-DEFINED ACADEMIC CREDENTIALS DATABASE ---
USERS_DB = {
    "CR-CSE-41": {"password": "cr41password", "role": "CR", "name": "CSE-41 CR", "batch": "CSE-41"},
    "CR-CSE-42": {"password": "cr42password", "role": "CR", "name": "CSE-42 CR", "batch": "CSE-42"},
    "T-CSE-RA": {"password": "teacher123", "role": "Teacher", "name": "Dr. Refat Ahmed", "batch": "Faculty"},
    "T-CSE-SK": {"password": "teacher456", "role": "Teacher", "name": "Prof. S. Khan", "batch": "Faculty"},
    "ADMIN-CSE": {"password": "adminrootpass", "role": "Admin", "name": "Dept Head / Admin", "batch": "Admin"}
}

BATCHES = ["CSE-41", "CSE-42", "CSE-43", "EEE-31", "EEE-32"]
CLASSROOMS = ["Room 101", "Room 102", "Room 201", "Lab 1", "Auditorium"]


# --- 2. AUTOMATIC DYNAMIC DATE & DAY GENERATION ---
def get_upcoming_week_dates():
    """Generates the next 7 days starting from today with exact dates."""
    today = datetime.now()
    dates_list = []
    for i in range(7):
        day_date = today + timedelta(days=i)
        # Format example: "Monday (Aug 31, 2026)"
        formatted = day_date.strftime("%A (%b %d, %Y)")
        dates_list.append(formatted)
    return dates_list


WEEK_DATES = get_upcoming_week_dates()

# Session State Initializations
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

if "bookings" not in st.session_state:
    st.session_state.bookings = [
        {
            "DateDay": WEEK_DATES[0],
            "Slot": "08:30 AM - 09:30 AM",
            "Classroom": "Room 101",
            "Batch": "CSE-41",
            "BookedBy": "CR-CSE-41",
            "Role": "CR",
            "Teacher": "Dr. Refat Ahmed"
        },
        {
            "DateDay": WEEK_DATES[0],
            "Slot": "10:30 AM - 11:30 AM",
            "Classroom": "Lab 1",
            "Batch": "CSE-42",
            "BookedBy": "T-CSE-SK",
            "Role": "Teacher",
            "Teacher": "Prof. S. Khan"
        }
    ]

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None


def get_slot_booking(dateday, slot, room):
    for b in st.session_state.bookings:
        if b["DateDay"] == dateday and b["Slot"] == slot and b["Classroom"] == room:
            return b
    return None


# --- 3. SECURE SIDEBAR AUTHENTICATION ---
st.sidebar.title("🔐 Department Portal")

if st.session_state.logged_user is None:
    st.sidebar.subheader("User Login")
    input_uid = st.sidebar.text_input("Unique ID", placeholder="e.g. CR-CSE-41, T-CSE-RA").strip()
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
            st.sidebar.error("Invalid Unique ID or Password!")
else:
    user = st.session_state.logged_user
    st.sidebar.success("🟢 **Logged In**")
    st.sidebar.markdown(f"**User:** {user['name']}\n\n**Role:** `{user['role']}`\n\n**ID:** `{user['uid']}`")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_user = None
        st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🏫 Classroom Booking & Schedule Portal")

# Configure dynamic tabs based on user role
logged_role = st.session_state.logged_user["role"] if st.session_state.logged_user else None

if logged_role == "Teacher":
    tab_teacher, tab1, tab2, tab3 = st.tabs(
        ["👨‍🏫 My Classes Today", "📅 Room Availability", "➕ Reserve Slot", "🔄 Free Slot"])
elif logged_role == "Admin":
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Room Availability", "➕ Reserve Slot", "🔄 Free Slot", "⚙️ Admin Routines"])
    tab_teacher = None
else:
    tab1, tab2, tab3 = st.tabs(["📅 Room Availability", "➕ Reserve Slot", "🔄 Free Slot"])
    tab_teacher = None

# --- NEW FEATURE 3: TEACHER PERSONAL SCHEDULE ---
if tab_teacher and logged_role == "Teacher":
    with tab_teacher:
        teacher_name = st.session_state.logged_user["name"]
        st.subheader(f"👨‍🏫 Assigned Classes for {teacher_name}")

        t_selected_date = st.selectbox("Select Date", WEEK_DATES, key="teacher_date_select")

        # Filter bookings matching logged-in teacher's name and selected date
        my_classes = [
            b for b in st.session_state.bookings
            if b["DateDay"] == t_selected_date and b["Teacher"].lower() == teacher_name.lower()
        ]

        if my_classes:
            st.markdown(f"#### You have **{len(my_classes)}** class(es) scheduled on {t_selected_date}:")
            for c in my_classes:
                st.info(
                    f"⏰ **{c['Slot']}** | 🏫 **Location:** {c['Classroom']} | "
                    f"🎓 **Batch:** {c['Batch']} (Booked by: `{c['BookedBy']}`)"
                )
        else:
            st.success(f"🎉 No classes scheduled for you on **{t_selected_date}**.")

# --- TAB 1: SCHEDULE & ROOM AVAILABILITY (WITH BATCH FILTERING) ---
with tab1:
    st.subheader("📅 Schedule & Availability Tracker")

    col_d, col_r = st.columns(2)
    with col_d:
        selected_date = st.selectbox("Select Date & Day", WEEK_DATES)
    with col_r:
        selected_room = st.selectbox("Select Classroom", CLASSROOMS)

    # NEW FEATURE 2: BATCH FILTERING FOR STUDENTS
    st.markdown("---")
    col_filter, _ = st.columns([1, 1])
    with col_filter:
        filter_batch = st.selectbox(
            "🔍 Filter Schedule by Batch (Optional):",
            ["All Batches"] + BATCHES
        )

    st.markdown(f"#### Matrix: **{selected_room}** on **{selected_date}**")

    for slot in st.session_state.time_slots:
        booking = get_slot_booking(selected_date, slot, selected_room)

        # Apply Batch Filter if selected
        if filter_batch != "All Batches" and booking and booking["Batch"] != filter_batch:
            continue

        with st.container():
            if booking:
                st.error(
                    f"🔴 **{slot}** | **Batch:** {booking['Batch']} | "
                    f"**Teacher:** {booking['Teacher']} (Reserved by `{booking['BookedBy']}`)"
                )
            else:
                st.success(f"🟢 **{slot}** | **Status:** Open for Booking")

# --- TAB 2: RESERVATION ---
with tab2:
    st.subheader("Reserve a Classroom Slot")

    if st.session_state.logged_user is None:
        st.warning("🔒 Please login from the sidebar using your Unique ID and Password to book slots.")
    else:
        current_user = st.session_state.logged_user

        with st.form("booking_form", clear_on_submit=True):
            st.info(f"Booking as: **{current_user['name']}** (`{current_user['role']}`)")

            b_date = st.selectbox("Date & Day", WEEK_DATES)
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
                if not assigned_teacher:
                    st.error("⚠️ Please specify the Conducting Teacher Name.")
                else:
                    existing = get_slot_booking(b_date, b_slot, b_room)
                    if existing:
                        st.error(f"❌ Slot already occupied by **{existing['Batch']}** ({existing['Teacher']}).")
                    else:
                        st.session_state.bookings.append({
                            "DateDay": b_date,
                            "Slot": b_slot,
                            "Classroom": b_room,
                            "Batch": target_batch,
                            "BookedBy": current_user["uid"],
                            "Role": current_user["role"],
                            "Teacher": assigned_teacher
                        })
                        st.success(f"✅ Reserved **{b_room}** on **{b_date} ({b_slot})**!")
                        st.rerun()

# --- TAB 3: CANCELLATION ---
with tab3:
    st.subheader("Free Up / Cancel a Scheduled Slot")

    if st.session_state.logged_user is None:
        st.warning("🔒 Please login from the sidebar to manage or cancel booked slots.")
    elif len(st.session_state.bookings) == 0:
        st.info("No active reservations exist in the system.")
    else:
        options = [
            f"{b['DateDay']} | {b['Slot']} | {b['Classroom']} | Batch: {b['Batch']} (Teacher: {b['Teacher']})"
            for b in st.session_state.bookings
        ]

        selected_cancel = st.selectbox("Select Class Slot to Cancel", options)

        if st.button("Cancel & Free Slot", type="primary", use_container_width=True):
            idx = options.index(selected_cancel)
            freed = st.session_state.bookings.pop(idx)
            st.success(f"🔓 Freed **{freed['Classroom']}** on **{freed['DateDay']} ({freed['Slot']})**.")
            st.rerun()

# --- TAB 4: ADMIN CONTROLS ---
if logged_role == "Admin" and tab4:
    with tab4:
        st.subheader("⚙️ Admin Semester Settings")
        st.markdown("##### Current Time Slots Configuration")

        updated_slots = []
        for i, slot in enumerate(st.session_state.time_slots):
            new_val = st.text_input(f"Slot #{i + 1}", value=slot, key=f"slot_cfg_{i}")
            updated_slots.append(new_val)

        col_admin1, col_admin2 = st.columns(2)
        with col_admin1:
            if st.button("💾 Save Updated Slot Timings", use_container_width=True):
                st.session_state.time_slots = updated_slots
                st.success("Slot timings updated globally!")
                st.rerun()

        with col_admin2:
            if st.button("⚠️ Reset All Bookings", type="primary", use_container_width=True):
                st.session_state.bookings = []
                st.success("All room bookings cleared!")
                st.rerun()

# --- 5. GLOBAL MASTER DATABASE TABLE ---
st.markdown("---")
with st.expander("📋 View Master Schedule Database"):
    if st.session_state.bookings:
        df = pd.DataFrame(st.session_state.bookings)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No active room reservations.")