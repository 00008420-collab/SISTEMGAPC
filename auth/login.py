# auth/login.py
import streamlit as st
import hashlib
from db import run_query
from auth.config import SESSION_USER_KEY

def hash_password(pw: str):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login_user():
    st.sidebar.title("Iniciar sesión")
    username = st.sidebar.text_input("Usuario", key="auth_user")
    password = st.sidebar.text_input("Contraseña", type="password", key="auth_pass")
    if st.sidebar.button("Iniciar sesión"):
        # buscar usuario en la tabla users (ajusta campos)
        sql = "SELECT id, username, nombre, correo, password_hash, id_tipo_usuario FROM users WHERE username=%s LIMIT 1"
        rows = run_query(sql, (username,))
        if not rows:
            st.sidebar.error("Usuario no encontrado")
            return False
        user = rows[0]
        # asumimos password_hash guarda SHA256 hex
        if user.get("password_hash") == hash_password(password):
            # login OK
            st.success(f"Bienvenido, {user.get('nombre') or username}")
            st.session_state[SESSION_USER_KEY] = {
                "id": user.get("id"),
                "username": user.get("username"),
                "nombre": user.get("nombre"),
                "correo": user.get("correo"),
                "id_tipo_usuario": user.get("id_tipo_usuario")
            }
            return True
        else:
            st.sidebar.error("Contraseña incorrecta")
            return False

def logout_user():
    if SESSION_USER_KEY in st.session_state:
        del st.session_state[SESSION_USER_KEY]
        st.experimental_rerun()

def current_user():
    return st.session_state.get(SESSION_USER_KEY)
