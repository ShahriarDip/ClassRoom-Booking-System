# views/teacher_view.py
import streamlit as st
from src.config import CLASSROOMS
from src.database import get_slot_status

def render_teacher_tab(week_dates_list, week_dates_dict):
    teacher_name = st.session_state.logged_user["name"]
    st.subheader(f"👨‍🏫 Assigned Schedule for {teacher_name}")
    t_selected_date = st.selectbox("Select Date", week_dates_list, key="t_date")
    
    my_classes = []
    for slot in st.session_state.time_slots:
        for room in CLASSROOMS:
            status = get_slot_status(t_selected_date, slot, room, week_dates_dict)
            if status and status["Teacher"].lower() == teacher_name.lower():
                my_classes.append(status)
                
    if my_classes:
        st.markdown(f"#### Scheduled classes for **{t_selected_date}**:")
        for c in my_classes:
            st.info(f"⏰ **{c['Slot']}** | 🏫 **{c['Classroom']}** | 🎓 **Batch:** {c['Batch']} | Type: `{c['Type']}`")
    else:
        st.success("🎉 No classes scheduled for you on this day.")
