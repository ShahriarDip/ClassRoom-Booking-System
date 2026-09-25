# views/availability.py
import streamlit as st
import pandas as pd
from src.config import CLASSROOMS, BATCHES
from src.database import (
    get_time_slots,
    get_master_routine,
    get_ad_hoc_bookings,
    get_slot_status
)


def render_availability_tab(week_dates_list, week_dates_dict):
    st.title("📅 Department Routine & Room Availability Tracker")

    # Fetch live data directly from Supabase DB
    all_slots = get_time_slots()
    master_routine = get_master_routine()
    ad_hoc_bookings = get_ad_hoc_bookings()

    if not all_slots:
        st.warning("⚠️ No time slots configured in database. Please configure time slots in Admin tab.")
        return

    # Header Filter Controls (Date & Batch Selector)
    col_date, col_batch = st.columns(2)
    with col_date:
        selected_date = st.selectbox(
            "📆 Select Date & Day",
            options=week_dates_list,
            index=0,
            key="avail_date_select"
        )
    with col_batch:
        batch_options = ["All Batches"] + BATCHES
        selected_batch = st.selectbox(
            "🎓 Filter by Academic Batch:",
            options=batch_options,
            index=0,
            key="avail_batch_select"
        )

    day_name = week_dates_dict[selected_date]

    # Calculate Filtered Metrics
    total_possible = len(all_slots) * len(CLASSROOMS)

    # Filter bookings by date and selected batch
    adhoc_today = [
        b for b in ad_hoc_bookings
        if b["DateDay"] == selected_date and (selected_batch == "All Batches" or b.get("Batch") == selected_batch)
    ]
    routine_today = [
        m for m in master_routine
        if m["Day"] == day_name and (selected_batch == "All Batches" or m.get("Batch") == selected_batch)
    ]

    adhoc_count = len(adhoc_today)
    routine_count = len(routine_today)
    total_occupied = routine_count + adhoc_count
    free_slots = max(0, total_possible - total_occupied)

    # Display Top Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Department Slots", total_possible)
    col2.metric("🟢 Free / Available", free_slots)
    col3.metric("🔴 Scheduled / Booked", routine_count)
    col4.metric("🟡 Ad-Hoc Reservations", adhoc_count)

    st.markdown("---")

    # --- SUB-TABS: MATRIX & ROOM EXPLORER ---
    sub_tab1, sub_tab2 = st.tabs(["📊 Full Occupancy Matrix", "🔍 Individual Room Explorer"])

    # =========================================================================
    # SUB-TAB 1: FULL OCCUPANCY MATRIX
    # =========================================================================
    with sub_tab1:
        st.markdown(f"### 📋 Complete Occupancy Grid for {day_name} ({selected_date})")
        st.caption("🟢 Green = Available for Ad-Hoc Booking | 🔴 Red = Occupied by Batch & Teacher")

        grid_rows = []
        for slot in all_slots:
            row_data = {"Time Slot": slot}
            for room in CLASSROOMS:
                status = get_slot_status(selected_date, slot, room, week_dates_dict)
                if status:
                    slot_batch = status.get("Batch", "")
                    if selected_batch != "All Batches" and slot_batch != selected_batch:
                        row_data[room] = "🟢 Free"
                    else:
                        teacher_info = f" ({status['Teacher']})" if status.get("Teacher") else ""
                        row_data[room] = f"🔴 {status['Batch']}{teacher_info}"
                else:
                    row_data[room] = "🟢 Free"
            grid_rows.append(row_data)

        df_grid = pd.DataFrame(grid_rows)
        st.dataframe(df_grid, width="stretch", hide_index=True)

        # CSV Download Button
        csv_data = df_grid.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Schedule as CSV",
            data=csv_data,
            file_name=f"classroom_occupancy_{selected_date}.csv",
            mime="text/csv"
        )

    # =========================================================================
    # SUB-TAB 2: INDIVIDUAL ROOM EXPLORER (SIDE-BY-SIDE CARDS)
    # =========================================================================
    with sub_tab2:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_room_filter = st.selectbox("Select Classroom to Inspect:", ["All Classrooms"] + CLASSROOMS,
                                                key="explorer_room_filter")
        with col_f2:
            selected_slot_filter = st.selectbox("Filter Time Slot:", ["All Slots"] + all_slots,
                                                key="explorer_slot_filter")

        rooms_to_show = CLASSROOMS if selected_room_filter == "All Classrooms" else [selected_room_filter]
        slots_to_show = all_slots if selected_slot_filter == "All Slots" else [selected_slot_filter]

        for room in rooms_to_show:
            with st.expander(f"📍 {room}", expanded=True):
                # Render cards in a 2-column side-by-side layout
                card_cols = st.columns(2)

                for idx, slot in enumerate(slots_to_show):
                    status = get_slot_status(selected_date, slot, room, week_dates_dict)
                    target_col = card_cols[idx % 2]

                    with target_col:
                        if status and (selected_batch == "All Batches" or status.get("Batch") == selected_batch):
                            # Red Card (Occupied)
                            st.markdown(f"""
                                <div style="
                                    background-color: #fde8e8;
                                    border-left: 5px solid #e53e3e;
                                    border-radius: 8px;
                                    padding: 12px;
                                    margin-bottom: 12px;
                                ">
                                    <strong style="color: #c53030;">🔴 {slot}</strong><br>
                                    <span style="color: #2d3748; font-weight: 500;">Batch: {status['Batch']}</span> | 
                                    <span style="color: #2d3748;">Faculty: {status.get('Teacher', 'N/A')}</span><br>
                                    <small style="color: #718096;">({status['Type']})</small>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Green Card (Available)
                            st.markdown(f"""
                                <div style="
                                    background-color: #f0fff4;
                                    border-left: 5px solid #38a169;
                                    border-radius: 8px;
                                    padding: 12px;
                                    margin-bottom: 12px;
                                ">
                                    <strong style="color: #276749;">🟢 {slot}</strong><br>
                                    <span style="color: #2f855a; font-weight: 500;">Available / Free</span>
                                </div>
                            """, unsafe_allow_html=True)