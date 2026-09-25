# views/teacher_view.py
import streamlit as st
from src.config import CLASSROOMS
from src.database import get_slot_status


def render_teacher_dashboard_tab(week_dates_list=None, week_dates_dict=None):
    st.subheader("👨‍🏫 Faculty Teaching Dashboard")

    if st.session_state.logged_user is None:
        st.warning("🔒 Please login from the sidebar using your Unique ID and Password.")
        return

    if week_dates_list is None:
        week_dates_list = st.session_state.get("week_dates_list", [])
    if week_dates_dict is None:
        week_dates_dict = st.session_state.get("week_dates_dict", {})

    current_user = st.session_state.logged_user
    teacher_name = current_user.get("name", "Dr. Refat Ahmed")

    # --- 1. FILTER CONTROLS ---
    col_fac, col_dt = st.columns(2)
    with col_fac:
        st.selectbox("Faculty Member:", [teacher_name], disabled=True)
    with col_dt:
        selected_date_filter = st.selectbox(
            "📅 Selected Date:",
            ["All 7 Upcoming Days"] + week_dates_list
        )

    # --- 2. QUERY TEACHER CLASSES ---
    target_dates = week_dates_list if selected_date_filter == "All 7 Upcoming Days" else [selected_date_filter]

    teacher_classes = []
    for date_str in target_dates:
        for room in CLASSROOMS:
            for slot in st.session_state.time_slots:
                booking = get_slot_status(date_str, slot, room, week_dates_dict)
                if booking and booking.get("Teacher") == teacher_name:
                    booking_info = dict(booking)
                    booking_info["DateDay"] = date_str
                    booking_info["Classroom"] = room
                    booking_info["Slot"] = slot
                    teacher_classes.append(booking_info)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. SUMMARY METRICS ---
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(
            f'''<div style="padding: 2px;">
                <span style="color: #4A5568; font-weight: 500; font-size: 0.88rem;">Scheduled Classes for {teacher_name}</span>
                <h2 style="margin: 2px 0 0 0; color: #1A202C; font-size: 2.2rem;">{len(teacher_classes)}</h2>
            </div>''',
            unsafe_allow_html=True
        )
    with col_m2:
        st.markdown(
            f'''<div style="padding: 2px;">
                <span style="color: #4A5568; font-weight: 500; font-size: 0.88rem;">Date Filter</span>
                <h2 style="margin: 2px 0 0 0; color: #1A202C; font-size: 1.8rem;">{selected_date_filter}</h2>
            </div>''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- 4. SCHEDULED CLASS TILES LIST ---
    st.markdown(f"### 📚 Scheduled Classes for **{teacher_name}**")
    st.markdown("<br>", unsafe_allow_html=True)

    if not teacher_classes:
        st.info(f"🎉 No scheduled classes found for {teacher_name} under '{selected_date_filter}'.")
        return

    for c in teacher_classes:
        b_type = c.get("Type", "Master Routine")
        booked_by = c.get("BookedBy", "Dept Master Routine")

        st.markdown(
            f'''
            <div style="background-color: #F7FAFC; border: 1px solid #E2E8F0; border-left: 5px solid #3182CE; padding: 14px 18px; border-radius: 8px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.98rem; font-weight: bold; color: #2D3748; margin-bottom: 6px;">
                            ⏰ {c["Slot"]} &nbsp;&nbsp;&nbsp; 📍 {c["Classroom"]} &nbsp;&nbsp;&nbsp; 🎓 <span style="color: #3182CE;">Batch: {c["Batch"]}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #718096;">
                            📅 <b>Date:</b> {c["DateDay"]} &nbsp;|&nbsp; 👤 <b>Booked by:</b> {booked_by}
                        </div>
                    </div>
                    <div>
                        <span style="background-color: #EBF8FF; color: #2B6CB0; padding: 6px 14px; border-radius: 16px; font-size: 0.8rem; font-weight: 600;">
                            {b_type}
                        </span>
                    </div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )