# views/admin_view.py
import streamlit as st
import pandas as pd
from src.config import DAYS, BATCHES, CLASSROOMS

def render_admin_tab():
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
