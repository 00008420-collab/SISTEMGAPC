# auth/login.py
import streamlit as st
import hashlib
from db import run_query

# -----------------------
# Helpers de hashing
# -----------------------
def sha256_hash(password: str) -> str:
    """Devuelve el hash SHA-256 en hex de la contraseña (compatible con SHA2 SQL)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def is_sha256_hash(s: str) -> bool:
    """Detecta heurísticamente si una cadena parece un SHA-256 hex (64 chars hex)."""
    if not isinstance(s, str):
        return False
    return len(s) == 64 and all(c in "0123456789abcdefABCDEF" for c in s)

# -----------------------
# Lógica de autenticación
# -----------------------
def login_user(username: str, password: str):
    """
    Intenta autenticar un usuario.
    Retorna (ok: bool, msg: str, user_row: dict|None).
    """
    if not username or not password:
        return False, "Ingrese usuario y contraseña.", None

    q = "SELECT * FROM users WHERE username = %s LIMIT 1"
    rows = run_query(q, (username,), fetch=True)
    if rows is None:
        return False, "Error al consultar la base de datos.", None
    if len(rows) == 0:
        return False, "Usuario no encontrado.", None

    user = rows[0]

    # Verificamos campo password_hash (nombres comunes: password_hash, password)
    stored = user.get("password_hash") or user.get("password") or ""
    stored = str(stored)

    # Si el hash almacenado parece SHA256 hex, verificamos
    if is_sha256_hash(stored):
        if sha256_hash(password) == stored:
            return True, "Autenticación correcta (SHA256).", user
        else:
            return False, "Contraseña incorrecta.", None

    # Si el hash no es SHA256 (ej: scrypt, bcrypt u otro formato) no podemos verificar aquí
    # Informamos al administrador que cree un usuario con SHA256 o use el registro por SQL.
    if stored:
        return False, (
            "No puedo verificar la contraseña porque el hash en la base de datos "
            "no es SHA256 (p. ej. scrypt/bcrypt). Crea un usuario con hash SHA256 "
            "o actualiza la contraseña del admin. Ejemplo SQL:\n\n"
            "UPDATE users SET password_hash = SHA2('tu_password',256) WHERE username='tu_usuario';"
        ), None

    return False, "El usuario no tiene contraseña almacenada.", None

# -----------------------
# UI - Caja de login
# -----------------------
def login_box():
    """
    Muestra el formulario de inicio de sesión. Si se autentica, guarda en st.session_state:
    - logged_in = True
    - user = user_row (diccionario)
    """
    # Inicializar session_state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None

    # Si ya está logueado, no mostrar el formulario
    if st.session_state.logged_in:
        st.success("Ya estás autenticado.")
        return

    # Layout elegante: dos columnas, texto a la izquierda, formulario a la derecha
    col_left, col_right = st.columns([1.4, 1])
    with col_left:
        st.markdown("## Welcome back")
        st.markdown(
            "Bienvenido(a). Inicia sesión para acceder al sistema. "
            "Si no tienes usuario pide al administrador crear uno con "
            "hash SHA256 (ej. `SHA2('contraseña',256)` en SQL)."
        )

    with col_right:
        st.markdown("### Sign in")
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        submit = st.button("Iniciar sesión")

        if submit:
            ok, msg, user_row = login_user(username.strip(), password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.user = user_row
                st.success(msg)
                # Rerun for z-index UI update / sidebar access
                st.rerun()
            else:
                # Mostrar error pero no recargar
                st.error(msg)

# -----------------------
# Requerir login desde páginas
# -----------------------
def require_login():
    """
    Si el usuario no ha iniciado sesión, muestra el login_box() y detiene la ejecución
    de la página (st.stop()). Si ya está, retorna el user_row.
    Uso: user = require_login()  -> luego usar user['id'], user['role'], etc.
    """
    if "logged_in" in st.session_state and st.session_state.logged_in:
        return st.session_state.user

    # No autenticado -> mostrar caja
    login_box()
    st.stop()
    return None  # nunca se alcanza por st.stop()

# -----------------------
# Logout simple
# -----------------------
def logout():
    """Cierra la sesión del usuario actual."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.success("Sesión cerrada.")
    st.rerun()

# -----------------------
# Si se importa y se usa directamente:
# -----------------------
if __name__ == "__main__":
    # Modo prueba: ejecuta la caja de login
    login_box()
