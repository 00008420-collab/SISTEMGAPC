# app.py
import streamlit as st
from db import test_connection, get_table_names
from auth.login import login_user, logout_user, current_user

st.set_page_config(page_title="SGAPC", layout="wide")
st.title("SGAPC - Menú principal")

# login
with st.sidebar:
    if "sgapc_user" not in st.session_state:
        login_user()
    else:
        u = current_user()
        st.markdown(f"**Conectado como:** {u.get('username')}")
        if st.button("Cerrar sesión"):
            logout_user()

# comprobación BD
ok, msg = test_connection()
if ok:
    st.success("Conexión establecida ✅")
    tables = get_table_names()
    st.write("Tablas detectadas:", ", ".join(tables))
else:
    st.error(f"Error conectando a la base de datos: {msg}")
    st.info("Revisa los secrets en Streamlit Cloud (Settings → Secrets).")

st.markdown("---")
st.markdown("Abre los CRUDs desde el menú lateral `Pages` o selecciona una Page.")
