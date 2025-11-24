# auth/login.py
import streamlit as st
from db import run_query
from auth.helpers import set_current_user, get_current_user

def _hash_password(pw: str) -> str:
    import hashlib
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login_box():
    """
    Muestra el formulario de login en la sidebar.
    Devuelve True si el usuario se autenticó correctamente (y ya quedó en session_state).
    NO llama a st.experimental_rerun() por sí misma.
    """
    with st.sidebar.form("login_form", clear_on_submit=False):
        st.write("### Iniciar sesión")
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        submitted = st.form_submit_button("Iniciar sesión")
        if submitted:
            ok = try_login(username.strip(), password)
            if ok:
                st.success("Inicio de sesión correcto")
                return True    # devolvemos True, no forzamos rerun aquí
            else:
                st.error("Usuario o contraseña incorrectos")
                return False
    return False

def try_login(username: str, password: str) -> bool:
    """Intenta autenticar contra la tabla users."""
    if not username or not password:
        return False

    rows = run_query(
        "SELECT id, username, full_name, email, password_hash, role FROM users WHERE username = %s LIMIT 1",
        (username,),
        fetch=True
    )
    if not rows:
        return False

    user = rows[0]
    db_hash = user.get("password_hash") or ""

    if db_hash == _hash_password(password):
        set_current_user({
            "id": user.get("id"),
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "role": user.get("role")
        })
        return True

    return False

def require_login():
    """
    Para usar en pages: si hay usuario devuelve el dict, si no lo hay muestra el login.
    Si el usuario acaba de autenticarse (login_box devolvió True), forzamos rerun aquí.
    """
    user = get_current_user()
    if user:
        return user

    just_logged = login_box()
    if just_logged:
        try:
            st.experimental_rerun()
        except Exception:
            # si experimental_rerun falla, devolvemos el user (ya seteado)
            return get_current_user()
    return None
