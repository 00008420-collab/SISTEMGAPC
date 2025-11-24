# auth/config.py
import streamlit as st

def check_login():
    """
    Llamar después de login_user() para verificar permisos básicos.
    Puedes ampliarlo para comprobar roles en la BD.
    """
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("No has iniciado sesión.")
        st.stop()

def require_role(role):
    """Ejemplo: comprobar rol (usa st.session_state['user'] con 'role')."""
    user = st.session_state.get("user", {})
    if user.get("role") != role:
        st.error("No tienes permisos para acceder a este recurso.")
        st.stop()
