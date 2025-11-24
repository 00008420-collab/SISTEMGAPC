# app.py
import streamlit as st
from typing import List, Optional, Tuple, Any
from db import run_query  # debe existir en tu repo
import html

st.set_page_config(
    page_title="SGAPC - Menú principal",
    layout="wide",
)

# -------------------------
# UTIL: consulta tablas
# -------------------------
def get_table_names_from_db() -> Optional[List[str]]:
    """Intenta obtener nombres de tablas. Usa SHOW TABLES si get_table_names no existe."""
    try:
        # Intentamos función común (si la tienes implementada en db.py)
        res = run_query("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()", fetch=True)
        if res:
            # res podría venir como lista de dicts o lista de tuples
            names = []
            for row in res:
                if isinstance(row, dict):
                    # toma la primera columna
                    first = next(iter(row.values()))
                    names.append(str(first))
                elif isinstance(row, (list, tuple)):
                    names.append(str(row[0]))
                else:
                    names.append(str(row))
            return names
    except Exception:
        pass

    # Fallback a SHOW TABLES
    try:
        res = run_query("SHOW TABLES", fetch=True)
        if not res:
            return []
        names = []
        for row in res:
            if isinstance(row, dict):
                first = next(iter(row.values()))
                names.append(str(first))
            elif isinstance(row, (list, tuple)):
                names.append(str(row[0]))
            else:
                names.append(str(row))
        return names
    except Exception as e:
        st.error(f"Error obteniendo tablas: {e}")
        return None

# -------------------------
# AUTENTICACIÓN
# -------------------------
def check_sha2_login(username: str, password: str) -> Optional[dict]:
    """
    Intenta autenticar usando SHA2 en MySQL:
    SELECT * FROM users WHERE username=%s AND password_hash=SHA2(%s,256)
    (funciona si en tu BD el password se guardó como SHA2(...,256))
    """
    try:
        q = """
        SELECT * FROM users
        WHERE username = %s AND password_hash = SHA2(%s,256)
        LIMIT 1
        """
        res = run_query(q, (username, password), fetch=True)
        if res:
            # devolver fila como dict o tuple
            return res[0]
    except Exception as e:
        # No detener; el método SHA2 no es obligatorio
        st.debug(f"SHA2 auth error: {e}")
    return None

def check_plain_or_direct(username: str, password: str) -> Optional[dict]:
    """
    Intenta autenticar comparando directamente el campo password_hash con el password ingresado.
    Esto ayuda si en tu tabla el password se almacenó en texto simple (no recomendado).
    """
    try:
        q = "SELECT * FROM users WHERE username = %s AND password_hash = %s LIMIT 1"
        res = run_query(q, (username, password), fetch=True)
        if res:
            return res[0]
    except Exception:
        pass
    return None

def user_exists(username: str) -> bool:
    try:
        q = "SELECT 1 FROM users WHERE username = %s LIMIT 1"
        res = run_query(q, (username,), fetch=True)
        return bool(res)
    except Exception:
        return False

def login_user(username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Intenta login con varios métodos. Devuelve (ok, mensaje, user_row_or_None)
    """
    # 1) Intentar SHA2 (recomendado si tus inserts usaron SHA2(...,256))
    row = check_sha2_login(username, password)
    if row:
        return True, "Autenticado (SHA2)", row

    # 2) Intentar comparación directa (no recomendado, pero por compatibilidad)
    row = check_plain_or_direct(username, password)
    if row:
        return True, "Autenticado (match directo)", row

    # 3) Si la cuenta existe pero no podemos validar (hash scrypt u otro), permitir si el usuario
    # ha configurado ADMIN_BYPASS en secrets (un token de emergencia).
    if user_exists(username):
        bypass = st.secrets.get("ADMIN_BYPASS", None)
        if bypass and password == bypass:
            row = run_query("SELECT * FROM users WHERE username = %s LIMIT 1", (username,), fetch=True)
            return True, "Autenticado con ADMIN_BYPASS (token en secrets)", row[0] if row else None

        # informar que la cuenta existe pero no se pudo verificar
        return False, ("La cuenta existe pero la app no pudo verificar la contraseña (hash no compatible). "
                       "Si quieres permitir login con este método, crea el usuario usando SHA2 en la BD "
                       "o añade ADMIN_BYPASS en secrets."), None

    # 4) no existe
    return False, "Usuario o contraseña incorrectos.", None

# -------------------------
# LAYOUT: LOGIN BONITO
# -------------------------
def show_login_page():
    st.markdown(
        """
        <style>
        /* fondo lateral e imagen hero si deseas (opcional) */
        .hero {
            padding: 40px;
            color: white;
        }
        .login-box {
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.4);
        }
        .big-title {
            font-size: 48px;
            font-weight:800;
            margin-bottom: 8px;
        }
        .muted {
            color: #cbd5e1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Layout: columnas (izquierda grande con hero, derecha estrecha con login)
    left_col, right_col = st.columns([2.6, 1])

    with left_col:
        st.markdown('<div class="big-title">Welcome Back</div>', unsafe_allow_html=True)
        st.markdown('<div class="muted">Bienvenido al sistema SGAPC. Inicia sesión para acceder al panel.</div>',
                    unsafe_allow_html=True)
        st.write("")  # espacio

    with right_col:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("Sign in")
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        remember = st.checkbox("Recordarme", key="login_remember")
        col1, col2 = st.columns([1, 1])
        with col1:
            login_btn = st.button("Iniciar sesión", key="login_btn")
        with col2:
            st.write("")  # placeholder para equilibrio
        st.markdown("</div>", unsafe_allow_html=True)

        # mensajes informativos
        st.write("")
        st.info("Si tu contraseña en la BD está hasheada con scrypt o con un esquema no compatible, "
                "usa la opción de creación de usuario con SHA2 o configura ADMIN_BYPASS en secrets.")

        return username, password, login_btn

# -------------------------
# PÁGINA PRINCIPAL POST-LOGIN
# -------------------------
def show_main_page(user_row: dict, table_names: List[str]):
    # menú superior / bienvenida
    st.markdown(f"### Bienvenido, **{html.escape(str(user_row.get('username', 'Usuario')))}**")
    st.write("Usa la barra lateral para abrir los CRUDs disponibles (Pages).")

    # Comprobación rápida de BD
    st.markdown("## 🔎 Comprobación rápida de la base de datos")
    st.success("Conexión establecida — Conexión OK")
    st.write("Tablas detectadas:")
    st.write(", ".join(table_names) if table_names else "No se detectaron tablas.")

    # Mostrar menú de acceso rápido (links a páginas, si deseas)
    st.markdown("---")
    st.markdown("### Atajos (haz clic para ver la Page desde el panel lateral)")
    for i, name in enumerate(table_names, start=1):
        # mostrar nombre amigable removiendo prefijo numérico si lo tuvieras
        pretty = name.replace("_", " ").title()
        st.write(f"- `{i:02d}` **{pretty}** ({name})")

# -------------------------
# MAIN
# -------------------------
def main():
    st.title("SGAPC - Menú principal")

    # Si ya hay sesión iniciada, mostrar main. Sino mostrar login.
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    # Si no conectado a DB: lo indicamos y paramos
    # Probamos una consulta simple para detectar si DB funciona (run_query debe estar OK)
    table_names = None
    try:
        table_names = get_table_names_from_db()
    except Exception as e:
        st.error(f"Error comprobando BD: {e}")

    # Si no logged_in -> mostrar login
    if not st.session_state.logged_in:
        username, password, login_btn = show_login_page()

        if login_btn:
            with st.spinner("Autenticando..."):
                ok, msg, user_row = login_user(username.strip(), password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user = user_row
                    st.success(msg)
                    # recargar la página para que el resto se muestre de forma "limpia"
                    st.experimental_rerun()
                else:
                    st.error(msg)
        else:
            # muestra estado de conexión (en la misma página de login)
            if table_names is None:
                st.warning("La aplicación no pudo comprobar la base de datos. Revisa los secrets y credenciales.")
            elif not table_names:
                st.info("Conexión establecida pero no se encontraron tablas (o no pudo listarlas).")
            else:
                # opcional: mostrar un pequeño resumen debajo del login
                st.info(f"Conexión OK — {len(table_names)} tablas detectadas.")
        return  # no ejecutar el resto hasta iniciar sesión

    # Si llegamos aquí, el usuario está autenticado
    user_row = st.session_state.user or {}
    # refrescar lista de tablas
    table_names = table_names or get_table_names_from_db() or []

    # show main
    show_main_page(user_row, table_names)

if __name__ == "__main__":
    main()
