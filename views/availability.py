# views/availability.py
import streamlit as st
from src.config import BATCHES, CLASSROOMS
from src.database import get_slot_status

def render_availability_tab(week_dates_list, week_dates_dict):
    st.subheader("📅 Classroom Routine & Availability Tracker")
    
    col_d, col_f = st.columns(2)
    with col_d:
        selected_date = st.selectbox("Select Date & Day", week_dates_list)
    with col_f:
        filter_batch = st.selectbox("🔍 Filter Schedule by Batch:", ["All Batches"] + BATCHES)

    st.markdown("---")

    if filter_batch != "All Batches":
        st.markdown(f"### 🎓 Full Daily Schedule for **{filter_batch}** ({selected_date})")
        st.caption("Showing all reserved classes across all classrooms and time slots.")
        
        batch_classes_found = []
        for slot in st.session_state.time_slots:
            for room in CLASSROOMS:
                booking = get_slot_status(selected_date, slot, room, week_dates_dict)
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
                booking = get_slot_status(selected_date, slot, room, week_dates_dict)
                if booking:
                    b_type = booking.get("Type", "Ad-hoc Booking")
                    st.error(
                        f"🔴 **{slot}** | **Batch:** {booking['Batch']} | "
                        f"**Teacher:** {booking['Teacher']} (`{b_type}`)"
                    )
                else:
                    st.success(f"🟢 **{slot}** | **Status:** Free / Open for Booking")
