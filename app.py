# app.py
import streamlit as st
from auth.login import require_login
from db import run_query
import crud_template_advanced as cta
import os

st.set_page_config(page_title="SGAPC - Portal", layout="wide")

# --- Configuración de roles: edita según tus roles y tablas ---
# las keys son nombres de rol en la tabla users.role (o user['role'])
# cada valor es lista de tables/pages que puede ver. Use '*' para todas.
role_permissions = {
    "administrador": ["*"],
    "promotora": ["grupo", "promotora", "reporte", "miembro"],
    "directiva": ["reunion", "miembro", "caja", "aportes", "reporte"],
    "miembro": ["miembro", "pago", "aporte"],
    # añade más conforme a tus necesidades
}

# --- utilidades ---
def tables_from_db():
    rows = run_query("SHOW TABLES;", fetch=True)
    if not rows:
        return []
    # la fila tiene key 'Tables_in_<database>'
    k = list(rows[0].keys())[0]
    return [r[k] for r in rows]

def allowed_tables_for_role(role, all_tables):
    perms = role_permissions.get(role, [])
    if "*" in perms:
        return sorted(all_tables)
    allowed = []
    for t in all_tables:
        if t in perms:
            allowed.append(t)
    return sorted(allowed)

# --- inicio ---
def main():
    st.title("SGAPC - Menú principal")
    user = require_login()  # si no está autenticado, require_login mostrará el login y detendrá el flujo

    # user es dict: leer role/username
    role = user.get("role") or user.get("rol") or user.get("role_name") or "usuario"
    username = user.get("username") or user.get("full_name") or "usuario"

    # Top bar
    st.sidebar.markdown(f"**Conectado:** {username} — _{role}_")
    st.sidebar.button("Cerrar sesión", on_click=lambda: (st.session_state.pop("user", None), st.experimental_rerun()))

    # intentamos conectar DB y listar tablas
    st.subheader("Comprobación rápida de la base de datos")
    tables = tables_from_db()
    if not tables:
        st.error("No se pudieron listar tablas. Revisa st.secrets['db'] y la conexión.")
    else:
        st.success("Conexión establecida ✅ — Conexión OK")

    # Filtrar tablas según rol
    allowed = allowed_tables_for_role(role, tables)

    # Sidebar: lista desplegable/expandible de tablas permitidas
    with st.sidebar.expander("GAPC — Menú", expanded=True):
        st.markdown("**Buscar...**")
        q = st.text_input("", key="sidebar_search")
        if q:
            filtered = [t for t in allowed if q.lower() in t.lower()]
        else:
            filtered = allowed
        # lista simplificada (sólo mostrar nombres bonitos)
        for t in filtered:
            pretty = t.replace("_", " ").title()
            if st.button(pretty, key=f"open_{t}"):
                # intentamos abrir la page mediante query param (no funciona en todas las versiones)
                st.experimental_set_query_params(page=t)
                st.experimental_rerun()

    # Main content: tarjetas resumen (puedes personalizar)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total tablas detectadas", len(tables))
    with col2:
        st.metric("Tablas disponibles para tu rol", len(allowed))
    with col3:
        st.write(" ")

    st.markdown("---")
    st.header("Tablas detectadas:")
    if tables:
        st.write(", ".join(tables))

    # Mostrar accesos rápidos (links a pages). En versiones antiguas no se abrirán automáticamente.
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Accesos Rápidos**")
    for t in allowed[:20]:
        pretty = t.replace("_", " ").title()
        st.sidebar.markdown(f"- {pretty}")

if __name__ == "__main__":
    main()
