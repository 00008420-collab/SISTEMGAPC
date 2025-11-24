# auth/login.py
import streamlit as st
from db import run_query  # asume que tienes run_query en db.py

def validate_user(username: str, password: str):
    """
    Valida credenciales contra la tabla users.
    Ajusta la consulta a tu esquema (hash usado).
    Ejemplo con SHA2:
    """
    if not username or not password:
        return None
    # Ajusta si usas otro esquema de hash; aquí se muestra SHA2 como ejemplo:
    q = "SELECT * FROM users WHERE username = %s AND password_hash = SHA2(%s,256) LIMIT 1"
    res = run_query(q, (username, password))
    if res and len(res) > 0:
        return res[0]
    return None

def login_box(prefix: str = "login"):
    """
    Muestra el formulario de login. Usa keys con prefijo para evitar colisiones.
    Retorna True si hizo login (y guardó user en session_state).
    """
    form_key = f"{prefix}_form"
    username_key = f"{prefix}_username"
    password_key = f"{prefix}_password"
    submit_key = f"{prefix}_submit"

    # Si ya hay usuario en session state, no dibujar el formulario
    if st.session_state.get("user"):
        return True

    with st.form(form_key):
        username = st.text_input("Usuario", key=username_key, placeholder="usuario", help="Ingresa tu usuario")
        password = st.text_input("Contraseña", type="password", key=password_key, placeholder="contraseña")
        submit = st.form_submit_button("Iniciar sesión", key=submit_key)

    if submit:
        user_row = validate_user(username, password)
        if user_row:
            st.session_state["user"] = user_row
            st.success(f"Bienvenido, {user_row.get('full_name', user_row.get('username'))}")
            # rerun para que el resto de app detecte el login
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña inválidos")
    return False

def require_login(prefix: str = "login"):
    """
    Si está logueado regresa user row; si no, muestra login_box y detiene la ejecución.
    - Llama login_box UNA VEZ. No duplicar calls a esta función.
    """
    if st.session_state.get("user"):
        return st.session_state["user"]

    # Mostrar el formulario en la barra lateral (o main) según prefieras
    st.sidebar.title("Iniciar sesión")
    login_box(prefix=prefix)

    # no hay user -> detener la ejecución de la página actual
    st.stop()
    return None
