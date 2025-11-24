import streamlit as st
SESSION_USER_KEY = "sgapc_user"

def set_current_user(user_dict):
    st.session_state[SESSION_USER_KEY] = user_dict

def get_current_user():
    return st.session_state.get(SESSION_USER_KEY)

def logout():
    if SESSION_USER_KEY in st.session_state:
        del st.session_state[SESSION_USER_KEY]
        st.experimental_rerun()
