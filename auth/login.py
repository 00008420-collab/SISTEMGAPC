# auth/login.py
import streamlit as st
from db import run_query
import hashlib

def hash_sha256(pw: str):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def fetch_user_by_username(username):
    rows = run_query("SELECT * FROM users WHERE username = %s LIMIT 1;", (username,), fetch=True)
    if rows:
        return rows[0]
    return None

def check_credentials(username, password):
    user = fetch_user_by_username(username)
    if not user:
        return None
    # tu columna password_hash debe contener el hex de sha256
    provided = hash_sha256(password)
    if provided == user.get("password_hash") or provided == user.get("password"):
        # some DBs store in 'password' o 'password_hash'
        return user
    return None

def login_box():
    st.subheader("Iniciar sesión")
    with st.form(key="login_form"):
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        submit = st.form_submit_button("Iniciar sesión")
    if submit:
        user = check_credentials(username.strip(), password)
        if user:
            st.session_state["user"] = user
            st.success("Autenticado (SHA2)")  # mensaje corto
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña inválida")

def require_login():
    """Si hay user en session_state la retorna; si no, muestra login y detiene ejecución."""
    if "user" in st.session_state:
        return st.session_state["user"]
    else:
        login_box()
        st.stop()
