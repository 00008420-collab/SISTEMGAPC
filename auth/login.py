import streamlit as st
from db import run_query
import hashlib

# Hash con SHA256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------
#   LOGIN BOX
# -------------------------

def login_box():
    st.markdown("<h2 style='text-align:center;'>Iniciar sesión</h2>", unsafe_allow_html=True)

    # 🟢 USAR KEYS ÚNICOS BASADOS EN SESSION_STATE
    if "login_username" not in st.session_state:
        st.session_state.login_username = ""
    if "login_password" not in st.session_state:
        st.session_state.login_password = ""

    username = st.text_input("Usuario", key="login_username_input")
    password = st.text_input("Contraseña", type="password", key="login_password_input")

    if st.button("Ingresar", key="login_button"):
        pw_hash = hash_password(password)
        user = run_query(
            "SELECT * FROM users WHERE username=%s AND password_hash=%s LIMIT 1",
            (username, pw_hash)
        )

        if user:
            st.session_state.user = user[0]
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")


# -------------------------
#   REQUIRE LOGIN
# -------------------------

def require_login():
    # Si no está autenticado, mostrar login
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        login_box()

        # ⚠️ detener la ejecución del resto de app.py
        st.stop()

    return st.session_state.user
