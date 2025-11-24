# auth/login.py
import streamlit as st
from db import run_query
from auth.helpers import set_current_user, get_current_user

def _hash_password(pw: str) -> str:
    # El sistema guarda SHA256
    import hashlib
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login_box():
    """Muestra el formulario de login en la sidebar (no detiene ejecución)."""
    with st.sidebar.form("login_form", clear_on_submit=False):
        st.write("### Iniciar sesión")
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        submitted = st.form_submit_button("Iniciar sesión")
        if submitted:
            success = try_login(username.strip(), password)
            if success:
                st.success("Inicio de sesión correcto")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def try_login(username: str, password: str) -> bool:
    """Intenta autenticar contra la tabla users (con esquema real)."""
    if not username or not password:
        return False

    # Consulta: usa las columnas que tienes (id, username, password_hash, full_name, email, role)
    rows = run_query(
        "SELECT id, username, full_name, email, password_hash, role FROM users WHERE username = %s LIMIT 1",
        (username,),
        fetch=True
    )
    if not rows:
        return False

    user = rows[0]
    db_hash = user.get("password_hash") or ""

    # Si tu DB almacena hash con SHA2(.,256) (hex), entonces comparamos con sha256 hex
    if db_hash == _hash_password(password):
        # Guardamos la mínima info en sesión
        set_current_user({
            "id": user.get("id"),
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "role": user.get("role")
        })
        return True

    # Si tu password_hash usa la forma 'scrypt:...' u otro, el check fallará; en ese caso
    # hay que adaptar la función de hashing al método que uses para ese usuario.
    return False

def require_login():
    """Útil para pages: devuelve el usuario si hay sesión, si no muestra login y devuelve None."""
    user = get_current_user()
    if user:
        return user
    # si no hay, mostramos el form (no rerun) y devolvemos None
    login_box()
    return None
