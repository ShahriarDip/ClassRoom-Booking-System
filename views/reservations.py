# views/reservations.py
import streamlit as st
from src.config import BATCHES, CLASSROOMS
from src.database import get_slot_status

def render_reservations_tab(week_dates_list, week_dates_dict):
    st.subheader("Reserve an Open Slot")
    if st.session_state.logged_user is None:
        st.warning("🔒 Please login from the sidebar using your Unique ID and Password.")
    else:
        current_user = st.session_state.logged_user
        
        with st.form("booking_form", clear_on_submit=True):
            st.info(f"Booking as: **{current_user['name']}** (`{current_user['role']}`)")
            
            b_date = st.selectbox("Date & Day", week_dates_list)
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
                existing = get_slot_status(b_date, b_slot, b_room, week_dates_dict)
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
