# app.py
import streamlit as st
from db import test_connection, get_table_names
from auth.login import require_login, login_box

st.set_page_config(page_title="SGAPC", layout="wide")

def hero_login():
    st.markdown(
        """
        <style>
        .hero {
            background: linear-gradient(90deg, rgba(10,25,47,1) 0%, rgba(3,37,65,1) 100%);
            padding: 50px;
            border-radius: 8px;
        }
        .hero h1 { font-size: 48px; margin-bottom: 10px; }
        .hero p { font-size: 16px; color: #ddd; }
        </style>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns([2, 1])

    with cols[0]:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown("## Bienvenido a SGAPC")
        st.markdown("Sistema para gestión de grupos. Inicia sesión para acceder.")
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        st.markdown("## Iniciar sesión")
        login_box(prefix="main")

def authenticated_ui():
    st.sidebar.title("Menú")
    st.sidebar.caption("Seleccione una sección")

    tables = get_table_names()

    with st.sidebar.expander("Tablas", expanded=True):
        if tables:
            for t in tables:
                name = t.replace("_", " ").title()
                st.markdown(f"- [{name}](?page={t})")
        else:
            st.info("No se encontraron tablas.")

    st.title("SGAPC — Portal")
    st.write("Bienvenido. Use el menú lateral.")

    ok, msg = test_connection()
    if ok:
        st.success(f"Conexión establecida — {msg}")
    else:
        st.error(f"Error de conexión — {msg}")

def main():
    # 🔥 Línea problemática eliminada 🔥
    # st.experimental_singleton.clear()

    if not st.session_state.get("user"):
        hero_login()
        st.stop()

    user = st.session_state["user"]
    st.sidebar.markdown(f"**Conectado como:** {user.get('username')}")

    authenticated_ui()

if __name__ == "__main__":
    main()
