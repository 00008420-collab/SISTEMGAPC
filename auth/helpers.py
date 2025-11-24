# auth/helpers.py
import streamlit as st

SESSION_KEY = "sgapc_user"

def get_current_user():
    return st.session_state.get(SESSION_KEY)

def set_current_user(user_dict: dict):
    st.session_state[SESSION_KEY] = user_dict

def logout():
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]
    # Forzar recarga
    st.experimental_rerun()
