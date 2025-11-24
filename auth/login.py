# auth/login.py
import streamlit as st

def authenticate(username, password):
    """
    Autenticación de ejemplo. Cambia esto por verificación real contra tu BD.
    Actualmente acepta cualquier usuario si la contraseña es 'secret'.
    """
    if username and password == "secret":
        return {"username": username, "role": "admin"}
    return None

def login_user():
    """
    Formulario de login minimalista. Guarda en st.session_state:
     - logged_in: bool
     - user: dict (username, role, ...)
    No usa st.experimental_rerun() para evitar errores en entornos donde no exista.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = {}

    st.sidebar.header("Iniciar sesión")
    with st.sidebar.form("login_form", clear_on_submit=False):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")
        if submitted:
            user = authenticate(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Bienvenido, {user['username']} ✅")
            else:
                st.error("Usuario/contraseña incorrectos. (contraseña de ejemplo: 'secret')")

    # Si ya está logueado, mostrar info compacta:
    if st.session_state.logged_in:
        user = st.session_state.get("user", {})
        st.sidebar.markdown(f"**Conectado como:** {user.get('username','-')}")
        if st.sidebar.button("Cerrar sesión"):
            st.session_state.logged_in = False
            st.session_state.user = {}
