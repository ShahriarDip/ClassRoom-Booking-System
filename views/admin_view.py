# views/admin_view.py
import streamlit as st
import pandas as pd
from datetime import time
from src.config import DAYS, BATCHES, CLASSROOMS, COURSES, TEACHERS_LIST
from src.database import (
    get_time_slots,
    add_time_slot,
    delete_time_slot,
    update_time_slot,
    get_master_routine,
    save_master_routine_grid,
    get_all_users,
    update_user_password,
    get_activity_logs,
    parse_slot_times
)


def render_admin_tab():
    st.subheader("⚙️ Department Master Admin Control Center")

    current_user = st.session_state.logged_user
    if not current_user or current_user["role"] != "Admin":
        st.error("🚫 Access Restricted to Department Admins.")
        return

    # --- 1. ADMIN USER PASSWORD MANAGEMENT SECTION ---
    with st.expander("🔑 Admin Password Reset & User Security Center", expanded=False):
        st.markdown("##### Change User Login Passwords")
        st.caption(
            "Only logged-in Admins can reset user passwords. All updates are encrypted via `bcrypt` in Supabase.")

        all_users = get_all_users()
        user_options = {f"{u['name']} ({u['uid']} - {u['role']})": u['uid'] for u in all_users}

        col_u, col_p = st.columns(2)
        with col_u:
            selected_user_label = st.selectbox("Select User Account:", list(user_options.keys()))
            selected_uid = user_options[selected_user_label]
        with col_p:
            new_pass = st.text_input("New Password", type="password", key="admin_new_pwd_input")

        if st.button("🔒 Update & Encrypt Password", type="primary", use_container_width=True):
            if not new_pass or len(new_pass.strip()) < 4:
                st.error("Password must be at least 4 characters long.")
            else:
                update_user_password(selected_uid, new_pass.strip(), current_user)
                st.success(f"✅ Successfully updated and encrypted password for **{selected_uid}**!")

    # --- 2. TIME SLOT MANAGEMENT SECTION ---
    with st.expander("⏰ Manage & Edit Department Time Slots", expanded=False):
        time_slots = get_time_slots()
        col_list, col_add = st.columns([1.2, 1])

        with col_list:
            st.markdown("**Current Database Slots:**")
            for idx, slot in enumerate(time_slots):
                c_slot, c_del = st.columns([3, 1])
                c_slot.code(slot)
                if c_del.button("❌", key=f"btn_del_{idx}"):
                    delete_time_slot(slot, current_user)
                    st.success(f"Removed slot: {slot}")
                    st.rerun()

        with col_add:
            st.markdown("**Add New Time Slot:**")
            with st.form("add_timeslot_form", clear_on_submit=True):
                col_st, col_et = st.columns(2)
                with col_st:
                    start_t = st.time_input("Start Time", value=time(8, 30))
                with col_et:
                    end_t = st.time_input("End Time", value=time(9, 30))

                if st.form_submit_button("➕ Add Time Slot", use_container_width=True):
                    new_slot_str = f"{start_t.strftime('%I:%M %p')} - {end_t.strftime('%I:%M %p')}"
                    add_time_slot(new_slot_str, current_user)
                    st.success(f"Added time slot: **{new_slot_str}**")
                    st.rerun()

    st.markdown("---")

    # --- 3. WEEKLY GRID MATRIX CONFIGURATION ---
    col_b, col_r = st.columns(2)
    with col_b:
        selected_batch = st.selectbox("Select Target Batch", BATCHES, key="admin_grid_batch")
    with col_r:
        selected_room = st.selectbox("Select Classroom", CLASSROOMS, key="admin_grid_room")

    st.markdown(f"#### 🗓️ Weekly Time Grid Matrix for **{selected_batch}** in **{selected_room}**")

    current_routine = get_master_routine()

    def find_routine_item(day, slot):
        for m in current_routine:
            if m["Day"] == day and m["Slot"] == slot and m["Classroom"] == selected_room and m[
                "Batch"] == selected_batch:
                return m
        return None

    time_slots = get_time_slots()
    grid_data = {}

    with st.form("weekly_grid_form"):
        day_tabs = st.tabs(DAYS)

        for idx, day in enumerate(DAYS):
            with day_tabs[idx]:
                grid_data[day] = {}
                for slot in time_slots:
                    existing_entry = find_routine_item(day, slot)
                    default_course = existing_entry["Course"] if existing_entry else "None (Free Slot)"
                    default_teacher = existing_entry["Teacher"] if existing_entry else "None"

                    course_idx = COURSES.index(default_course) if default_course in COURSES else 0
                    teacher_idx = TEACHERS_LIST.index(default_teacher) if default_teacher in TEACHERS_LIST else 0

                    col1, col2, col3 = st.columns([2, 3, 3])
                    col1.caption(f"⏰ {slot}")
                    c_val = col2.selectbox("Course", COURSES, index=course_idx,
                                           key=f"c_{selected_batch}_{selected_room}_{day}_{slot}",
                                           label_visibility="collapsed")
                    t_val = col3.selectbox("Teacher", TEACHERS_LIST, index=teacher_idx,
                                           key=f"t_{selected_batch}_{selected_room}_{day}_{slot}",
                                           label_visibility="collapsed")

                    grid_data[day][slot] = {"course": c_val, "teacher": t_val}

        if st.form_submit_button("💾 Save Master Routine Grid to Supabase", use_container_width=True, type="primary"):
            new_entries = []
            for day, slots in grid_data.items():
                for slot, info in slots.items():
                    if info["course"] != "None (Free Slot)":
                        new_entries.append({
                            "day": day,
                            "slot": slot,
                            "classroom": selected_room,
                            "batch": selected_batch,
                            "course": info["course"],
                            "teacher": info["teacher"]
                        })

            save_master_routine_grid(selected_batch, selected_room, new_entries, current_user)
            st.success("✅ Saved routine matrix to Supabase!")
            st.rerun()

    st.markdown("---")

    # --- 4. LIVE AUDIT LOGS ---
    st.markdown("##### 📜 Live System Activity & Change Logs")
    logs = get_activity_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs)[["created_at", "uid", "user_name", "role", "action", "details"]],
                     use_container_width=True)