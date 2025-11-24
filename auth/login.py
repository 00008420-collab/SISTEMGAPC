# auth/login.py
import streamlit as st
from db import run_query
from auth import load_permissions_for_role, get_user_role_id
import hashlib

def hash_password(raw):
    # simple hashing: usa en pruebas. En producción usa bcrypt.
    return hashlib.sha256(raw.encode()).hexdigest()

def verify_password(username, raw_password):
    # compara hash (asume password_hash en users)
    rows = run_query("SELECT password_hash FROM users WHERE username=%s LIMIT 1", params=(username,), fetch=True)
    if not rows:
        return False
    stored = rows[0].get("password_hash")
    return stored == hash_password(raw_password)

def login_user():
    st.sidebar.header("Iniciar sesión")
    if "user" in st.session_state:
        st.sidebar.markdown(f"Conectado como: **{st.session_state['user']}**")
        if st.sidebar.button("Cerrar sesión"):
            for k in ["user", "permissions", "role_id"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.experimental_rerun()
        return

    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Iniciar sesión"):
        # aquí puedes validar con password real
        if verify_password(username, password):
            st.session_state["user"] = username
            role_id = get_user_role_id(username)
            st.session_state["role_id"] = role_id
            st.session_state["permissions"] = load_permissions_for_role(role_id)
            st.sidebar.success(f"Bienvenido, {username}")
            st.experimental_rerun()
        else:
            st.sidebar.error("Usuario o contraseña incorrectos.")
