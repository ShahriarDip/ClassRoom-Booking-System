# views/cancellations.py
import streamlit as st
from src.database import get_ad_hoc_bookings, delete_ad_hoc_booking

def render_cancellations_tab(week_dates_list, week_dates_dict):
    st.subheader("🔄 Free / Cancel Ad-Hoc Room Reservations")

    user = st.session_state.logged_user
    if not user:
        st.warning("🔒 Please log in from the sidebar to view and manage your reservations.")
        return

    # Fetch all ad-hoc bookings
    all_bookings = get_ad_hoc_bookings()

    # Filter bookings based on user permissions
    # Admins see all; CRs/Teachers see reservations they booked or match their batch/name
    if user["role"] == "Admin":
        user_bookings = all_bookings
    elif user["role"] == "CR":
        user_bookings = [
            b for b in all_bookings
            if b.get("Batch") == user.get("batch") or b.get("BookedBy") == user["uid"]
        ]
    else:  # Teacher
        user_bookings = [
            b for b in all_bookings
            if b.get("Teacher") == user["name"] or b.get("BookedBy") == user["uid"]
        ]

    if not user_bookings:
        st.info("ℹ️ You have no active ad-hoc reservations to cancel.")
        return

    st.markdown("---")

    for b in user_bookings:
        booking_id = b["id"]
        date_day = b.get("DateDay", "N/A")
        slot = b.get("Slot", "N/A")
        classroom = b.get("Classroom", "N/A")
        batch = b.get("Batch", "N/A")
        teacher = b.get("Teacher", "N/A")
        booked_by = b.get("BookedBy", "N/A")

        col_card, col_action = st.columns([4, 1], vertical_alignment="center")

        with col_card:
            # Custom styled container with explicit dark text colors for high readability
            st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    border: 1px solid #e2e8f0;
                    border-left: 6px solid #e53e3e;
                    border-radius: 8px;
                    padding: 14px 18px;
                    margin-bottom: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #1a202c; margin-bottom: 4px;">
                        📍 {classroom} &nbsp;|&nbsp; ⏰ {slot}
                    </div>
                    <div style="font-size: 0.95rem; color: #2d3748; margin-bottom: 2px;">
                        📅 <strong>Date:</strong> {date_day} &nbsp;|&nbsp; 🎓 <strong>Batch:</strong> {batch}
                    </div>
                    <div style="font-size: 0.85rem; color: #4a5568;">
                        👨‍🏫 <strong>Teacher:</strong> {teacher} &nbsp;|&nbsp; 👤 <strong>Booked By:</strong> {booked_by}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col_action:
            if st.button("🗑️ Free Slot", key=f"free_btn_{booking_id}"):
                delete_ad_hoc_booking(booking_id, user)
                st.success(f"Successfully freed {classroom} ({slot})!")
                st.rerun()

    st.markdown("---")