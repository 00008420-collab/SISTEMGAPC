# auth/login.py
import streamlit as st
import hashlib
from db import run_query

# Prefijo de keys para evitar duplicados
KEY_PREFIX = "auth_"

def _hash_password_sha256(password: str) -> str:
    """Hash simple SHA-256 (hex). Usado para comparar con valores almacenados como SHA2(...,256)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_user_by_username(username: str):
    """Obtiene el registro de user por username. Retorna dict o None."""
    try:
        rows = run_query("SELECT * FROM users WHERE username = %s LIMIT 1", (username,))
        if rows:
            return rows[0]
    except Exception as e:
        st.error(f"Error al consultar usuario: {e}")
    return None

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifica la contraseña contra el hash almacenado.
    - Si stored_hash parece hex de 64 chars (SHA256), compara con sha256(plain_password).
    - Si stored_hash comienza con "scrypt:" (u otro prefijo), devolvemos False y mostramos aviso.
    - Si stored_hash es None o vacío -> False.
    """
    if not stored_hash:
        return False

    # caso SHA256 en hex (64 caracteres hex)
    if isinstance(stored_hash, str) and len(stored_hash) == 64 and all(c in "0123456789abcdef" for c in stored_hash.lower()):
        return _hash_password_sha256(plain_password) == stored_hash.lower()

    # Posibles otros formatos (ej: "scrypt:...") -> no podemos verificar aquí
    if isinstance(stored_hash, str) and stored_hash.startswith("scrypt:"):
        # si tus usuarios usan scrypt, indica cómo crear/admin el usuario o implementa verificación scrypt
        st.warning("El hash de la contraseña usa 'scrypt' — la verificación automática no está implementada. Crea un usuario con SHA256 para pruebas.")
        return False

    # último intento: comparar directamente (no recomendado)
    return plain_password == stored_hash

def login_box():
    """
    Muestra el formulario de login. Si autenticación correcta, guarda en st.session_state['user'] el row dict.
    No hace st.experimental_rerun para evitar errores con ciertas versiones.
    """
    st.subheader("Iniciar sesión")
    col1, col2 = st.columns([2, 1])

    with col1:
        username = st.text_input("Usuario", key=KEY_PREFIX + "username")
        password = st.text_input("Contraseña", type="password", key=KEY_PREFIX + "password")
    with col2:
        st.caption("Acceso al sistema")
        if st.button("Iniciar sesión", key=KEY_PREFIX + "btn_login"):
            if not username or not password:
                st.error("Ingresa usuario y contraseña.")
                return False

            user_row = get_user_by_username(username)
            if not user_row:
                st.error("Usuario no encontrado.")
                return False

            stored_hash = user_row.get("password_hash") or user_row.get("password") or user_row.get("passwordhash")
            if verify_password(password, stored_hash):
                # Guarda datos útiles en session_state
                st.session_state["user"] = {
                    "id": user_row.get("id") or user_row.get("id_user") or user_row.get("id_usuario"),
                    "username": user_row.get("username"),
                    "full_name": user_row.get("full_name") or user_row.get("nombre") or user_row.get("nombre_completo"),
                    "email": user_row.get("email") or user_row.get("correo"),
                    "role": user_row.get("role") or user_row.get("rol") or user_row.get("id_role"),
                    "raw_row": user_row
                }
                st.success(f"Bienvenido, {st.session_state['user']['username']} ✅")
                # No hacemos experimental_rerun: la app seguirá, y require_login() hará st.stop() si no hay user
                return True
            else:
                st.error("Contraseña incorrecta.")
                return False

    # mostrar enlace a recuperar contraseña o instrucciones si quieres
    st.markdown("¿Olvidaste tu contraseña? Contacta al administrador.")

    return False

def logout():
    """Cierra sesión."""
    for k in list(st.session_state.keys()):
        # borrar sólo claves relacionadas con auth y la key user
        if k.startswith(KEY_PREFIX) or k == "user":
            del st.session_state[k]
    st.success("Sesión cerrada.")

def require_login():
    """
    Llamar al comienzo de pages que requieren autenticación:
        user = require_login()
    - Si ya hay usuario en session_state, retorna esa info.
    - Si no, muestra el login y detiene la ejecución con st.stop() hasta que el usuario inicie sesión.
    """
    # si ya autenticado, devuelve user
    if st.session_state.get("user"):
        return st.session_state["user"]

    # si no, mostrar login form
    logged = login_box()
    # Si login_box devolvió True, se habrá escrito session_state['user'] — retornamos
    if st.session_state.get("user"):
        return st.session_state["user"]

    # no autenticado -> parar ejecución del resto de la page
    st.warning("Debes iniciar sesión para continuar.")
    st.stop()
