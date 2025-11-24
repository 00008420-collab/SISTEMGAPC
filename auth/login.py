# auth/login.py
import streamlit as st
from auth.config import AUTH_TABLE, AUTH_USER_COL, AUTH_PASS_COL, PASSWORD_HASH, SESSION_KEY
from db import get_connection

def _verify_password(stored, provided):
    if stored is None:
        return False
    if PASSWORD_HASH == "plain":
        return stored == provided
    elif PASSWORD_HASH == "bcrypt":
        import bcrypt
        try:
            return bcrypt.checkpw(provided.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            return False
    else:
        return stored == provided

def _fetch_user(row_user):
    """
    Retorna fila del administrador si existe, como dict.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            sql = f"SELECT * FROM `{AUTH_TABLE}` WHERE `{AUTH_USER_COL}` = %s LIMIT 1"
            cur.execute(sql, (row_user,))
            row = cur.fetchone()
            return row
    except Exception as e:
        st.error(f"Error consultando tabla de administradores: {e}")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass

def logout():
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]

def show_login_streamlit():
    """
    Muestra formulario de login en Streamlit.  
    Si el usuario ya está en sesión devuelve su identificador (email o nombre).
    Si inicia sesión y es correcto, guarda en st.session_state[SESSION_KEY] y devuelve usuario.
    Si no hay conexión, muestra error y devuelve None.
    """
    # si ya autenticado
    if SESSION_KEY in st.session_state and st.session_state.get(SESSION_KEY):
        return st.session_state[SESSION_KEY]

    st.sidebar.header("🔐 Iniciar sesión")
    with st.sidebar.form("login_form"):
        user = st.text_input("Usuario (email)", value="")
        pwd = st.text_input("Contraseña", type="password", value="")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            if not user or not pwd:
                st.sidebar.warning("Ingresa usuario y contraseña.")
            else:
                row = _fetch_user(user)
                if not row:
                    st.sidebar.error("Usuario no encontrado.")
                else:
                    stored = row.get(AUTH_PASS_COL)
                    if _verify_password(stored, pwd):
                        st.session_state[SESSION_KEY] = user
                        st.sidebar.success(f"Bienvenido, {user}")
                        return user
                    else:
                        st.sidebar.error("Credenciales incorrectas.")
    # si no enviado, devuelve None
    return None
