# app.py
import streamlit as st
from db import test_connection, get_table_names, run_query, get_role_permissions_from_db
import hashlib

st.set_page_config(page_title="SGAPC - Portal", layout="wide", initial_sidebar_state="collapsed")

# ----------------- CSS -----------------
STYLE = """
<style>
/* hero */
.hero {
  background: linear-gradient(90deg,#071428 0%, #0b2b44 100%);
  padding: 28px;
  border-radius: 8px;
  color: #fff;
}
.hero h1 { font-size: 42px; margin:0 0 4px 0; }
.hero p { color: #cfe3f5; margin:0; }

/* card */
.card {
  background: rgba(255,255,255,0.02);
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.03);
}
.small-muted { color:#98a6b3; font-size:13px; }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ----------------- AUTH helpers -----------------
def hash_sha256(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()

def get_user_by_username(username: str):
    """
    Lee usuario de la tabla 'users'. Ajusta nombres de columnas si los tienes distintos.
    Espera columns: id, username, password_hash, full_name, email, role
    """
    q = "SELECT id, username, password_hash, full_name, email, role FROM users WHERE username = %s LIMIT 1;"
    rows = run_query(q, (username,), fetch=True)
    if not rows:
        return None
    return rows[0]

def verify_credentials_db(username: str, password: str):
    """
    Verifica contra la BD usando SHA-256 (ajusta si usas scrypt/bcrypt).
    Retorna user dict o None.
    """
    user = get_user_by_username(username)
    if not user:
        return None
    stored = user.get("password_hash") or ""
    # si tu stored ya contiene 'scrypt:' u otro formato, hay que adaptar.
    # aquí suponemos hex SHA256
    if stored == hash_sha256(password):
        return user
    # si almacenaste con SHA2(mysql) (hex 64) funcionará.
    return None

# ----------------- Login UI -----------------
def login_center(key_prefix="login"):
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown("<h1>SGAPC — Iniciar sesión</h1>", unsafe_allow_html=True)
    st.markdown("<p>Introduce tus credenciales para continuar</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 0.7, 1])
    with col2:
        uname = st.text_input("Usuario", key=f"{key_prefix}_username")
        pwd = st.text_input("Contraseña", type="password", key=f"{key_prefix}_password")
        if st.button("Iniciar sesión", key=f"{key_prefix}_submit"):
            user = verify_credentials_db(uname, pwd)
            if user:
                # Guarda datos mínimos en sesión
                st.session_state["user"] = {
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "full_name": user.get("full_name") or user.get("username"),
                    "role": user.get("role") or "user"
                }
                st.success(f"Autenticado ({user.get('role')})")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# ----------------- Sidebar / Navegación -----------------
def sidebar_menu(all_tables, allowed_tables):
    st.sidebar.title("GAPC — Menú")
    q = st.sidebar.text_input("Buscar...", key="sidebar_search")
    filtered = [t for t in allowed_tables if q.lower() in t.lower()] if q else allowed_tables

    st.sidebar.markdown("### Pages")
    for t in filtered:
        label = t.replace("_", " ").title()
        # abrir página real: en Streamlit <latest> no hay navegación programática estable,
        # usaremos botones que ponen en session_state['open_table']
        if st.sidebar.button(label, key=f"btn_{t}"):
            st.session_state["open_table"] = t
            st.experimental_rerun()

    st.sidebar.markdown("---")
    if st.session_state.get("user"):
        st.sidebar.write(f"Conectado: **{st.session_state['user']['username']}**")
        if st.sidebar.button("Cerrar sesión", key="logout_btn"):
            st.session_state.pop("user", None)
            st.session_state.pop("open_table", None)
            st.experimental_rerun()

# ----------------- Dashboard UI -----------------
def show_dashboard(tables):
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown("<h1>SGAPC - Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p>Bienvenido al sistema. Usa el menú lateral para abrir las tablas.</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("")

    ok, msg = test_connection()
    if ok:
        st.success("Conexión establecida ✅ — " + msg)
    else:
        st.error("Error de conexión: " + msg)

    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="card"><h3>Actas</h3><div class="small-muted">Registro de actas y reuniones</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="card"><h3>Miembros</h3><div class="small-muted">Gestión de miembros</div></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown('<div class="card"><h3>Préstamos</h3><div class="small-muted">Control y pagos</div></div>', unsafe_allow_html=True)

    st.markdown("### Tablas detectadas:")
    st.write(", ".join(tables) if tables else "—")

# ----------------- Role -> allowed tables mapping (fallback) -----------------
# EDITA según tus reglas si no quieres usar la tabla role_permission
role_table_map = {
    "administrador": [],  # empty = acceso a todo
    "promotora": ["promotora","grupo","miembro","reunion"],
    "directiva": ["directiva","reunion","caja","aporte","pago"],
    "miembro": ["miembro","aporte","pago","prestamo"],
    "user": ["miembro"]  # ejemplo
}

def compute_allowed_tables(role, all_tables):
    """
    Intenta leer role_permissions desde DB; si no existe, usa role_table_map fallback.
    Si role tiene lista vacía en role_table_map -> significa 'todo'.
    """
    perms = get_role_permissions_from_db()
    if perms:
        allowed = perms.get(role)
        if allowed is None:
            # si rol no definido en DB, denegar todo (o dar todo si prefieres)
            return []
        # filtrar solo tablas existentes
        return [t for t in allowed if t in all_tables]

    # fallback a role_table_map (hardcode)
    if role in role_table_map:
        allowed = role_table_map[role]
        if allowed == []:  # [] → todo
            return all_tables
        return [t for t in allowed if t in all_tables]
    # rol desconocido -> sin acceso
    return []

# ----------------- Main -----------------
def main():
    # si ya autenticado mostramos todo; si no, pedimos login
    if not st.session_state.get("user"):
        login_center(key_prefix="main")
        st.stop()

    user = st.session_state["user"]
    all_tables = get_table_names()
    # compute allowed
    allowed = compute_allowed_tables(user.get("role"), all_tables)

    # sidebar con solo allowed
    sidebar_menu(all_tables, allowed)

    # si se pidió abrir tabla específica (session_state['open_table']), mostrar placeholder
    open_t = st.session_state.get("open_table")
    if open_t:
        st.header(open_t.replace("_", " ").title())
        st.write("Aquí irá el CRUD de la tabla:", open_t)
        st.write(" (Implementa la carga de la Page correspondiente o queries específicas)")
        st.stop()

    show_dashboard(all_tables)

if __name__ == "__main__":
    main()
