# src/auth.py
import streamlit as st
from src.config import USERS_DB

def render_sidebar_login():
    st.sidebar.title("🔐 EEE Portal Login")

    if st.session_state.logged_user is None:
        st.sidebar.subheader("User Login")
        input_uid = st.sidebar.text_input("Unique ID", placeholder="e.g. CR-EEE-41, ADMIN-EEE").strip()
        input_pwd = st.sidebar.text_input("Password", type="password").strip()
        
        if st.sidebar.button("Login", type="primary", use_container_width=True):
            if input_uid in USERS_DB and USERS_DB[input_uid]["password"] == input_pwd:
                st.session_state.logged_user = {
                    "uid": input_uid,
                    "role": USERS_DB[input_uid]["role"],
                    "name": USERS_DB[input_uid]["name"],
                    "batch": USERS_DB[input_uid]["batch"]
                }
                st.sidebar.success(f"Welcome, {USERS_DB[input_uid]['name']}!")
                st.rerun()
            else:
                st.sidebar.error("Invalid Credentials!")
    else:
        user = st.session_state.logged_user
        st.sidebar.success("🟢 **Logged In**")
        st.sidebar.markdown(f"**User:** {user['name']}\n\n**Role:** `{user['role']}`\n\n**ID:** `{user['uid']}`")
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_user = None
            st.rerun()
