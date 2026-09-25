# views/reservations.py
import streamlit as st
from src.config import BATCHES, CLASSROOMS, TEACHERS_LIST
from src.database import get_slot_status, add_ad_hoc_booking, get_time_slots


def render_reservations_tab(week_dates_list=None, week_dates_dict=None):
    st.subheader("➕ Reserve an Open Classroom Slot")

    if st.session_state.logged_user is None:
        st.warning("🔒 Please login from the sidebar using your Unique ID and Password.")
        return

    current_user = st.session_state.logged_user
    time_slots = get_time_slots()

    with st.form("booking_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        b_date = col1.selectbox("📅 Reservation Date", week_dates_list)
        b_room = col2.selectbox("🏫 Desired Classroom / Lab", CLASSROOMS)

        col3, col4 = st.columns(2)
        b_slot = col3.selectbox("⏰ Desired Time Slot", time_slots)

        if current_user["role"] == "CR":
            target_batch = col4.text_input("🎓 Target Batch", value=current_user["batch"], disabled=True)
        else:
            target_batch = col4.selectbox("🎓 Target Batch", BATCHES)

        if current_user["role"] == "Teacher":
            assigned_teacher = st.text_input("👨‍🏫 Conducting Teacher", value=current_user["name"], disabled=True)
        else:
            default_t_idx = TEACHERS_LIST.index(current_user["name"]) if current_user["name"] in TEACHERS_LIST else 0
            assigned_teacher = st.selectbox("👨‍🏫 Conducting Teacher", TEACHERS_LIST, index=default_t_idx)

        submit_btn = st.form_submit_button("⚡ Confirm Reservation to Supabase", use_container_width=True,
                                           type="primary")

        if submit_btn:
            existing = get_slot_status(b_date, b_slot, b_room, week_dates_dict)
            if existing:
                st.error(f"❌ Slot occupied by **{existing['Batch']}** ({existing['Teacher']}).")
            else:
                add_ad_hoc_booking({
                    "DateDay": b_date,
                    "Slot": b_slot,
                    "Classroom": b_room,
                    "Batch": target_batch,
                    "BookedBy": current_user["uid"],
                    "Role": current_user["role"],
                    "Teacher": assigned_teacher,
                    "Type": "CR/Teacher Reserve"
                }, current_user)
                st.success("✅ Slot reserved and saved to Supabase!")
                st.rerun()