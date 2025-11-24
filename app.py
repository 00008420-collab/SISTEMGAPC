# app.py
import streamlit as st
from typing import List, Optional, Dict, Any
from db import (
    test_connection,
    get_table_names,
    get_role_permissions_by_role,
    get_user_by_username,
    run_query,
)

import hashlib

# -------------------------
# Utilidades de autenticación (SHA256)
# -------------------------
def verify_password_sha256(plain_text: str, stored_hash: str) -> bool:
    """
    Verifica password con SHA256 (hex digest).
    Si tu stored_hash usa otro esquema (bcrypt/scrypt) reemplazar por la lógica adecuada.
    """
    if not plain_text or not stored_hash:
        return False
    digest = hashlib.sha256(plain_text.encode("utf-8")).hexdigest()
    return digest == stored_hash

# -------------------------
# Inicialización de estado
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None  # user dict desde DB cuando autenticado
if "selected_table" not in st.session_state:
    st.session_state.selected_table = None
if "tables" not in st.session_state:
    st.session_state.tables = []
if "visible_tables" not in st.session_state:
    st.session_state.visible_tables = []

# -------------------------
# Layout / estilos mínimos
# -------------------------
st.set_page_config(page_title="SGAPC - Portal", layout="wide")

# Estilos CSS mínimos (puedes personalizar)
st.markdown(
    """
    <style>
    .hero {
        padding: 12px 24px;
        border-radius: 8px;
        background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        margin-bottom: 16px;
    }
    .card {
        padding: 18px;
        border-radius: 10px;
        background-color: rgba(255,255,255,0.02);
        margin-bottom: 18px;
    }
    .sidebar-title {
        font-size:16px;
        font-weight:700;
        margin-top:12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Login form (pantalla principal de inicio)
# -------------------------
def show_login():
    st.title("SGAPC — Portal")
    st.write("Bienvenido. Inicia sesión para acceder al sistema.")
    col1, col2 = st.columns([1, 2])
    with col1:
        # vacio a propósito (diseño)
        st.empty()
    with col2:
        with st.form(key="login_form", clear_on_submit=False):
            st.subheader("Iniciar sesión")
            username = st.text_input("Usuario", key="login_username")
            password = st.text_input("Contraseña", type="password", key="login_password")
            submitted = st.form_submit_button("Iniciar sesión")
            if submitted:
                if not username or not password:
                    st.error("Completa usuario y contraseña.")
                else:
                    user_row = get_user_by_username(username)
                    if not user_row:
                        st.error("Usuario no encontrado.")
                    else:
                        # buscar posibles columnas con hash
                        stored = user_row.get("password_hash") or user_row.get("password") or user_row.get("password_h")
                        if stored is None:
                            st.error("Usuario sin contraseña registrada.")
                        else:
                            ok = verify_password_sha256(password, stored)
                            if ok:
                                # set session
                                st.session_state.user = user_row
                                st.success(f"Bienvenido, {user_row.get('full_name') or user_row.get('username')}")
                                # al logear, cargar tablas y permisos
                                load_tables_for_user()
                            else:
                                st.error("Contraseña incorrecta.")

# -------------------------
# Cargar tablas (según rol)
# -------------------------
def load_tables_for_user():
    """
    Llama get_table_names y filtra por permisos si hay role/role_permission.
    Guarda en session_state.visible_tables
    """
    tables = get_table_names() or []
    st.session_state.tables = tables

    # Si no hay usuario autenticado, no mostramos tablas
    if not st.session_state.user:
        st.session_state.visible_tables = []
        return

    # Detectar rol en user row; puede estar en columna 'role' o 'id_role'
    role_name = None
    if "role" in st.session_state.user and st.session_state.user.get("role"):
        role_name = st.session_state.user.get("role")
    elif "id_role" in st.session_state.user and st.session_state.user.get("id_role"):
        # si solo hay id, podrías hacer consulta para obtener name; por simplicidad usamos id as str
        role_name = str(st.session_state.user.get("id_role"))

    if role_name:
        try:
            allowed = get_role_permissions_by_role(role_name) or []
            # si role_permission no existe o devuelve vacío, asumimos acceso completo
            if len(allowed) == 0:
                # si no hay rows de permisos, mostrar todo
                st.session_state.visible_tables = tables
            else:
                # Filtrar solo los que estan permitidos y existen en la BD
                st.session_state.visible_tables = [t for t in tables if t in allowed]
        except Exception:
            st.session_state.visible_tables = tables
    else:
        # sin role: por seguridad no mostrar nada
        st.session_state.visible_tables = []

# -------------------------
# Sidebar: buscador + lista de tablas
# -------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("## GAPC — Menú")
        if st.session_state.user:
            st.markdown(f"**Conectado:** {st.session_state.user.get('username')}")
            # Buscar
            q = st.text_input("Buscar page o tabla...", key="side_search")
            # Show tables list (expandable)
            visible = st.session_state.visible_tables or []
            if not visible:
                st.info("No tienes tablas visibles o no se detectaron permisos.")
            else:
                # Opción de ver X primero y 'View more'
                max_show = 12
                filtered = [t for t in visible if q.lower() in t.lower()] if q else visible
                show_list = filtered[: max_show]
                for tbl in show_list:
                    # cada botón tiene un key único para evitar duplicados
                    if st.button(tbl, key=f"btn_tbl_{tbl}"):
                        st.session_state.selected_table = tbl
                if len(filtered) > max_show:
                    if st.button("View more", key="view_more_tables"):
                        # si aprieta view more, mostramos todo (simplemente reemplazamos lista)
                        for tbl in filtered[max_show:]:
                            if st.button(tbl, key=f"btn_tbl_more_{tbl}"):
                                st.session_state.selected_table = tbl

            st.markdown("---")
            if st.button("Cerrar sesión", key="btn_logout"):
                st.session_state.user = None
                st.session_state.selected_table = None
                st.session_state.visible_tables = []
                st.experimental_rerun()
        else:
            st.info("Debes iniciar sesión para ver el menú y las tablas.")

# -------------------------
# Main content (después de login)
# -------------------------
def show_main():
    # Header
    st.markdown('<div class="hero"><h1>SGAPC - Menú principal</h1></div>', unsafe_allow_html=True)
    if not st.session_state.user:
        # Si no está autenticado, mostramos login en main y detenemos
        show_login()
        return

    # Si estamos autenticados, mostramos panel principal con comprobación BD
    ok, msg = test_connection()
    if ok:
        st.success(f"Conexión establecida ✅ — {msg}")
    else:
        st.error(f"Error de conexión a la BD: {msg}")

    # Mostrar tarjetas de acceso rápido (estético)
    st.markdown("### Accesos rápidos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h3>Actas</h3><p>Registro de actas y reuniones</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>Miembros</h3><p>Gestión de miembros</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h3>Préstamos</h3><p>Control y pagos</p></div>', unsafe_allow_html=True)

    # Mostrar tablas detectadas
    st.markdown("### Tablas detectadas:")
    tables_display = st.session_state.tables or []
    if not tables_display:
        st.write("_No se detectaron tablas_")
    else:
        st.write(", ".join(tables_display))

    # Si se seleccionó una tabla en el sidebar, mostrar preview simple (SELECT * LIMIT 10)
    if st.session_state.selected_table:
        tbl = st.session_state.selected_table
        st.markdown(f"### Vista rápida: `{tbl}`")
        try:
            rows = run_query(f"SELECT * FROM `{tbl}` LIMIT 10", fetch=True)
            if rows is None:
                st.warning("No se pudo obtener filas o query falló.")
            elif len(rows) == 0:
                st.info("Tabla vacía o no hay registros.")
            else:
                # Mostrar tabla resultante
                st.dataframe(rows)
        except Exception as e:
            st.error(f"Error al mostrar tabla {tbl}: {e}")

# -------------------------
# Punto de entrada
# -------------------------
def main():
    show_sidebar()
    show_main()

# Ejecutar
if __name__ == "__main__":
    main()
