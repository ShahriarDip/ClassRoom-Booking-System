# src/database.py
import streamlit as st
import bcrypt
from datetime import datetime, timedelta, time
from supabase import create_client, Client


def get_supabase_client() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)


supabase = get_supabase_client()


# --- SECURITY & HASHING ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# --- ACTIVITY / AUDIT LOGGING ---
def log_activity(uid: str, name: str, role: str, action: str, details: str = ""):
    try:
        supabase.table("activity_logs").insert({
            "uid": uid,
            "user_name": name,
            "role": role,
            "action": action,
            "details": details
        }).execute()
        st.cache_data.clear()  # Clear cache so new activity logs appear immediately
    except Exception as e:
        st.error(f"Failed to record activity log: {e}")


@st.cache_data(ttl=60)
def get_activity_logs(limit: int = 50):
    res = supabase.table("activity_logs").select("*").order("created_at", desc=True).limit(limit).execute()
    return res.data or []


# --- USERS MANAGEMENT ---
@st.cache_data(ttl=60)
def get_user_by_uid(uid: str):
    res = supabase.table("users").select("*").eq("uid", uid).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    return None


@st.cache_data(ttl=60)
def get_all_users():
    res = supabase.table("users").select("uid, role, name, batch").execute()
    return res.data or []


def update_user_password(target_uid: str, new_password: str, admin_user: dict):
    new_hash = hash_password(new_password)
    supabase.table("users").update({
        "password_hash": new_hash,
        "updated_at": "now()"
    }).eq("uid", target_uid).execute()

    st.cache_data.clear()  # Invalidate user cache

    log_activity(
        uid=admin_user["uid"],
        name=admin_user["name"],
        role=admin_user["role"],
        action="PASSWORD_RESET",
        details=f"Reset password for user {target_uid}"
    )


# --- TIME SLOTS ---
def parse_slot_times(slot_str):
    try:
        start_str, end_str = slot_str.split(" - ")
        start_t = datetime.strptime(start_str.strip(), "%I:%M %p").time()
        end_t = datetime.strptime(end_str.strip(), "%I:%M %p").time()
        return start_t, end_t
    except Exception:
        return None, None


@st.cache_data(ttl=60)
def get_time_slots():
    res = supabase.table("time_slots").select("slot_str").order("id").execute()
    if res.data:
        return [item["slot_str"] for item in res.data]
    return []


def add_time_slot(new_slot_str: str, user: dict):
    supabase.table("time_slots").insert({"slot_str": new_slot_str}).execute()
    st.cache_data.clear()  # Invalidate slots cache
    log_activity(user["uid"], user["name"], user["role"], "ADD_TIME_SLOT", f"Added slot: {new_slot_str}")


def delete_time_slot(slot_str: str, user: dict):
    supabase.table("time_slots").delete().eq("slot_str", slot_str).execute()
    supabase.table("master_routine").delete().eq("slot", slot_str).execute()
    st.cache_data.clear()  # Invalidate slots & routine cache
    log_activity(user["uid"], user["name"], user["role"], "DELETE_TIME_SLOT", f"Deleted slot: {slot_str}")


def update_time_slot(old_slot: str, new_slot: str, user: dict):
    supabase.table("time_slots").update({"slot_str": new_slot}).eq("slot_str", old_slot).execute()
    supabase.table("master_routine").update({"slot": new_slot}).eq("slot", old_slot).execute()
    supabase.table("ad_hoc_bookings").update({"slot": new_slot}).eq("slot", old_slot).execute()
    st.cache_data.clear()  # Invalidate all table caches
    log_activity(user["uid"], user["name"], user["role"], "EDIT_TIME_SLOT",
                 f"Updated slot from {old_slot} to {new_slot}")


# --- MASTER ROUTINE & BOOKINGS ---
@st.cache_data(ttl=60)
def get_master_routine():
    res = supabase.table("master_routine").select("*").execute()
    formatted = []
    for r in (res.data or []):
        formatted.append({
            "Day": r["day"],
            "Slot": r["slot"],
            "Classroom": r["classroom"],
            "Batch": r["batch"],
            "Course": r["course"],
            "Teacher": r["teacher"],
            "Type": "Master Routine"
        })
    return formatted


@st.cache_data(ttl=60)
def get_ad_hoc_bookings():
    res = supabase.table("ad_hoc_bookings").select("*").execute()
    formatted = []
    for b in (res.data or []):
        formatted.append({
            "id": b["id"],
            "DateDay": b["date_day"],
            "Slot": b["slot"],
            "Classroom": b["classroom"],
            "Batch": b["batch"],
            "BookedBy": b["booked_by"],
            "Role": b["role"],
            "Teacher": b["teacher"],
            "Type": b["booking_type"],
            "timestamp": b["created_at"]
        })
    return formatted


def add_ad_hoc_booking(booking_data: dict, user: dict):
    res = supabase.table("ad_hoc_bookings").insert({
        "date_day": booking_data["DateDay"],
        "slot": booking_data["Slot"],
        "classroom": booking_data["Classroom"],
        "batch": booking_data["Batch"],
        "booked_by": booking_data["BookedBy"],
        "role": booking_data["Role"],
        "teacher": booking_data["Teacher"],
        "booking_type": booking_data["Type"]
    }).execute()

    st.cache_data.clear()  # Invalidate bookings cache

    log_activity(
        user["uid"], user["name"], user["role"], "RESERVE_SLOT",
        f"Reserved {booking_data['Classroom']} on {booking_data['DateDay']} ({booking_data['Slot']})"
    )
    return res


def delete_ad_hoc_booking(booking_id: str, user: dict):
    supabase.table("ad_hoc_bookings").delete().eq("id", booking_id).execute()
    st.cache_data.clear()  # Invalidate bookings cache
    log_activity(
        user["uid"], user["name"], user["role"], "FREE_SLOT",
        f"Freed reservation ID: {booking_id}"
    )


def save_master_routine_grid(selected_batch: str, selected_room: str, entries: list, user: dict):
    # Remove existing entries for target batch & room
    supabase.table("master_routine").delete().eq("batch", selected_batch).eq("classroom", selected_room).execute()

    if entries:
        supabase.table("master_routine").insert(entries).execute()

    st.cache_data.clear()  # Invalidate master routine cache

    log_activity(
        user["uid"], user["name"], user["role"], "UPDATE_MASTER_ROUTINE",
        f"Updated routine grid for {selected_batch} in {selected_room}"
    )


@st.cache_data(ttl=60)
def get_upcoming_week_dates():
    today = datetime.now()
    dates_dict = {}
    for i in range(7):
        d = today + timedelta(days=i)
        dates_dict[d.strftime("%A (%b %d, %Y)")] = d.strftime("%A")
    return dates_dict


def init_session_state():
    if "logged_user" not in st.session_state:
        st.session_state.logged_user = None


# Note: Do not add @st.cache_data here as it computes logic in-memory using cached readers
def get_slot_status(dateday_str, slot, room, week_dates_dict):
    day_name = week_dates_dict[dateday_str]
    adhoc = get_ad_hoc_bookings()
    for b in adhoc:
        if b["DateDay"] == dateday_str and b["Slot"] == slot and b["Classroom"] == room:
            return b

    master = get_master_routine()
    for m in master:
        if m["Day"] == day_name and m["Slot"] == slot and m["Classroom"] == room:
            return {
                "DateDay": dateday_str,
                "Slot": slot,
                "Classroom": room,
                "Batch": m["Batch"],
                "Course": m.get("Course", "N/A"),
                "Teacher": m["Teacher"],
                "BookedBy": "Dept Routine",
                "Type": "Master Routine"
            }
    return None