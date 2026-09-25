import streamlit as st
import pandas as pd
import os

from src.database import init_session_state, get_upcoming_week_dates, get_master_routine
from src.auth import render_sidebar_login

from views.availability import render_availability_tab
from views.reservations import render_reservations_tab
from views.cancellations import render_cancellations_tab
from views.teacher_view import render_teacher_dashboard_tab
from views.admin_view import render_admin_tab

st.set_page_config(
    page_title="EEE SUST - Classroom Booking System",
    page_icon="🏫",
    layout="wide"
)

init_session_state()
week_dates_dict = get_upcoming_week_dates()
week_dates_list = list(week_dates_dict.keys())

# Store in session state for view fallback safety
st.session_state.week_dates_dict = week_dates_dict
st.session_state.week_dates_list = week_dates_list

col_logo1, col_header, col_logo2 = st.columns([1, 4, 1])

with col_logo1:
    if os.path.exists("assets/logo_sust.png"):
        st.image("assets/logo_sust.png", width=110)
    else:
        st.write("🏫 **SUST**")

with col_header:
    st.title("Department of EEE, SUST")
    st.subheader("Classroom Routine & Smart Booking Control System")
    st.caption("Shahjalal University of Science and Technology, Sylhet")

with col_logo2:
    if os.path.exists("assets/logo_eee.png"):
        st.image("assets/logo_eee.png", width=110)
    else:
        st.write("⚡ **EEE**")

st.markdown("---")

render_sidebar_login()

logged_role = st.session_state.logged_user["role"] if st.session_state.logged_user else None

# Pre-initialize tab variables
tab_teacher = None
tab_admin = None

if logged_role == "Teacher":
    tab_teacher, tab1, tab2, tab3 = st.tabs(["👨‍🏫 My Classes Today", "📅 Availability Matrix", "➕ Reserve Extra Slot", "🔄 Free/Cancel Slot"])
elif logged_role == "Admin":
    tab1, tab2, tab3, tab_admin = st.tabs(["📅 Availability Matrix", "➕ Reserve Extra Slot", "🔄 Free/Cancel Slot", "⚙️ Admin Master Routine"])
else:
    tab1, tab2, tab3 = st.tabs(["📅 Availability Matrix", "➕ Reserve Extra Slot", "🔄 Free/Cancel Slot"])

if tab_teacher and logged_role == "Teacher":
    with tab_teacher:
        render_teacher_dashboard_tab(week_dates_list, week_dates_dict)

with tab1:
    render_availability_tab(week_dates_list, week_dates_dict)

with tab2:
    render_reservations_tab(week_dates_list, week_dates_dict)

with tab3:
    render_cancellations_tab(week_dates_list, week_dates_dict)

if logged_role == "Admin" and tab_admin:
    with tab_admin:
        render_admin_tab()

st.markdown("---")
with st.expander("📋 View Master Semester Schedule Data"):
    master_data = get_master_routine()
    if master_data:
        st.dataframe(pd.DataFrame(master_data), width="stretch")
    else:
        st.info("No master routine data found in Supabase database.")