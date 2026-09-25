# src/auth.py
import streamlit as st
from src.database import get_user_by_uid, verify_password

def render_sidebar_login():
    if "logged_user" not in st.session_state:
        st.session_state.logged_user = None

    if st.session_state.logged_user:
        user = st.session_state.logged_user
        st.sidebar.success(f"Logged in as **{user['name']}** ({user['role']})")
        if st.sidebar.button("Logout", key="logout_btn"):
            st.session_state.logged_user = None
            st.rerun()
        return

    st.sidebar.title("🔐 Portal Login")
    uid_input = st.sidebar.text_input("Unique ID", key="login_uid").strip().upper()
    password_input = st.sidebar.text_input("Password", type="password", key="login_pwd")

    if st.sidebar.button("Login", key="login_submit_btn"):
        if not uid_input or not password_input:
            st.sidebar.error("Please enter both ID and Password.")
            return

        # Force clear cache on login attempt to read live data from Supabase
        st.cache_data.clear()

        user = get_user_by_uid(uid_input)

        if user and verify_password(password_input, user.get("password_hash", "")):
            st.session_state.logged_user = user
            st.sidebar.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials!")