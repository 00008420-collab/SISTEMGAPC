import streamlit as st
from db import test_connection, get_table_names
from auth.login import login_box, require_login
from auth.helpers import get_current_user, logout

st.set_page_config(page_title="SGAPC", layout="wide")
st.title("SGAPC - Menú principal")

# Sidebar auth
with st.sidebar:
    user = get_current_user()
    if not user:
        login_box()
        st.stop()
    else:
        st.markdown(f"**Conectado como:** {user.get('username')}")
        if st.button("Cerrar sesión"):
            logout()

# Quick DB check
st.header("Comprobación rápida de la base de datos")
if test_connection():
    st.success("Conexión establecida ✅")
    tables = get_table_names() or []
    st.write("Tablas detectadas:")
    st.write(", ".join(tables))
else:
    st.error("No se pudo conectar a la base de datos. Revisa Streamlit Secrets.")

st.markdown("---")
st.markdown("Abre las Pages desde el menú lateral `Pages` para ver los CRUDs.")
