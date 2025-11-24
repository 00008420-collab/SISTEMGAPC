# app.py
import streamlit as st
from db import test_connection, get_table_names

st.set_page_config(page_title="SGAPC - Menú", layout="wide")

def show_header():
    st.markdown("# 📘 SGAPC - Menú principal")
    st.write("Bienvenido al sistema. Usa el menú lateral (Pages) para abrir los CRUDs.")

def show_db_check():
    st.markdown("## 🔍 Comprobación rápida de la base de datos")
    ok, msg = test_connection()
    if ok:
        st.success("Conexión establecida ✅ — " + msg)
        tables = get_table_names()
        if tables:
            st.markdown("**Tablas detectadas:**")
            st.write(", ".join(tables))
        else:
            st.info("Conexión OK pero no se pudieron listar tablas (get_table_names devolvió None).")
    else:
        st.error("Error de conexión a la BD: " + msg)
        st.warning("Revisa los secrets (Settings -> Secrets) y reinicia la app.")

def sidebar_navigation(tables):
    st.sidebar.markdown("### 🔧 Navegación")
    q = st.sidebar.text_input("Buscar page o tabla...")
    st.sidebar.markdown("**Pages:**")
    # Si tu versión de Streamlit soporta Pages, el menú lateral de la izquierda ya tiene las pages.
    # Aquí listamos enlaces rápidos (solo info). No podemos forzar navegación desde app.py de forma portable.
    if tables:
        # crear un expander con la lista de tablas para estética
        with st.sidebar.expander("Ver tablas"):
            for t in tables:
                if q and q.lower() not in t.lower():
                    continue
                st.markdown(f"- {t}")

def shortcuts_panel(tables):
    st.markdown("## 🧭 Atajos")
    st.write("Accesos rápidos a Pages (haz clic para abrir). Si tu versión de Streamlit soporta navegación automática, se abrirán.")
    if not tables:
        st.info("No hay tablas listadas para generar atajos.")
        return
    for i, t in enumerate(tables, start=1):
        page_name = f"{i:02d}_{t}_crud"
        # mostrar como enlace (no siempre navegará automáticamente)
        st.markdown(f"- [{page_name}](./?page={page_name})  \n  `{t}`")

def main():
    show_header()

    # intentar mostrar login si existe el módulo auth con require_login
    user = None
    try:
        from auth.login import require_login
        user = require_login()
    except Exception:
        # Si el módulo de auth no existe o lanza error, no interrumpimos la app.
        user = None

    # Panel principal: comprobación DB y atajos
    cols = st.columns([3,1])
    with cols[0]:
        show_db_check()
    with cols[1]:
        # get_table_names solo para la sidebar/atajos si conexión ok
        ok, msg = test_connection()
        tables = []
        if ok:
            tables = get_table_names() or []
        shortcuts_panel(tables)

    # Sidebar navigation (presentable)
    sidebar_navigation(tables if 'tables' in locals() else None)

    # Mensaje final
    if user:
        st.success(f"Conectado como: {user}")
    else:
        st.info("No se inició sesión (login opcional).")

if __name__ == "__main__":
    main()
