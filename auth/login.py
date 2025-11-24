import streamlit as st
import hashlib
from db import run_query
from auth.helpers import set_current_user, get_current_user, logout

def _hash_password(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def login_box():
    user = get_current_user()
    if user:
        return user

    with st.sidebar.form("login_form", clear_on_submit=False):
        st.write("### Iniciar sesión")
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        submitted = st.form_submit_button("Iniciar sesión")
        if submitted:
            rows = run_query("SELECT id, username, nombre, correo, password_hash, id_tipo_usuario FROM users WHERE username=%s LIMIT 1", (username,))
            if not rows:
                st.sidebar.error("Usuario no encontrado")
                return None
            u = rows[0]
            if u.get("password_hash") == _hash_password(password):
                set_current_user({
                    "id": u.get("id"),
                    "username": u.get("username"),
                    "nombre": u.get("nombre"),
                    "correo": u.get("correo"),
                    "id_tipo_usuario": u.get("id_tipo_usuario")
                })
                st.sidebar.success("Autenticado")
                st.experimental_rerun()
            else:
                st.sidebar.error("Contraseña incorrecta")
                return None

    return None

def require_login():
    user = get_current_user()
    if not user:
        user = login_box()
    return user
