# views/cancellations.py
import streamlit as st

def render_cancellations_tab():
    st.subheader("Free Up / Cancel a Booking")
    if st.session_state.logged_user is None:
        st.warning("🔒 Please login to manage or cancel slots.")
    else:
        if st.session_state.ad_hoc_bookings:
            opts = [f"{b['DateDay']} | {b['Slot']} | {b['Classroom']} | Batch: {b['Batch']}" for b in st.session_state.ad_hoc_bookings]
            selected_cancel = st.selectbox("Select Extra Booking to Free", opts)
            
            if st.button("Cancel Selected Booking", type="primary", use_container_width=True):
                idx = opts.index(selected_cancel)
                st.session_state.ad_hoc_bookings.pop(idx)
                st.success("🔓 Reserved slot freed successfully!")
                st.rerun()
        else:
            st.info("No active extra reservations to cancel.")
