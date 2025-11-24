# auth/login.py
import streamlit as st
from db import run_query

def validate_user(username: str, password: str):
    """
    Valida credenciales contra la tabla users.
    Ajusta si tu DB usa otro esquema de hash.
    """
    if not username or not password:
        return None
    # EJEMPLO con SHA2: reemplaza si usas bcrypt/scrypt etc.
    q = "SELECT * FROM users WHERE username = %s AND password_hash = SHA2(%s,256) LIMIT 1"
    res = run_query(q, (username, password))
    if res and len(res) > 0:
        return res[0]
    return None

def login_box(prefix: str = "login"):
    """
    Muestra formulario de login (usa prefix para keys).
    Retorna True si exitoso (user guardado en session_state).
    """
    username_key = f"{prefix}_username"
    password_key = f"{prefix}_password"
    submit_key = f"{prefix}_submit"
    form_key = f"{prefix}_form"

    # Si ya está autenticado no dibujar el formulario
    if st.session_state.get("user"):
        return True

    with st.form(form_key):
        st.write("")  # para espaciado
        username = st.text_input("Usuario", key=username_key, placeholder="usuario")
        password = st.text_input("Contraseña", type="password", key=password_key, placeholder="contraseña")
        submitted = st.form_submit_button("Iniciar sesión", key=submit_key)

    if submitted:
        user_row = validate_user(username, password)
        if user_row:
            st.session_state["user"] = user_row
            # mensaje y rerun para que la app recargue y muestre la interfaz autenticada
            st.success(f"Bienvenido, {user_row.get('full_name', user_row.get('username'))}")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña inválidos")
    return False

def require_login(prefix: str = "login"):
    """
    Llama login_box en sidebar y para ejecución si no hay sesión.
    Retorna la fila user (dict) si está autenticado, o detiene la ejecución si no.
    """
    if st.session_state.get("user"):
        return st.session_state["user"]

    # Mostrar en la barra lateral (puedes cambiar a main si prefieres)
    st.sidebar.title("Iniciar sesión")
    login_box(prefix=prefix)
    # Si no hay user, detener la página aquí (hasta que haga login)
    st.stop()
    return None
