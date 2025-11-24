# app.py
import streamlit as st
from db import test_connection, get_table_names
from auth.login import login_box, require_login
from auth.helpers import get_current_user, logout

st.set_page_config(page_title="SGAPC", layout="wide")
st.title("SGAPC - Menú principal")

# -----------------------------------
# SIDEBAR: login y usuario
# -----------------------------------
with st.sidebar:
    user = get_current_user()
    if not user:
        # muestra el formulario de login (esto no permite ver nada hasta iniciar sesión)
        login_box()
        # si no se ha autenticado, detenemos la ejecución del main para que no vea nada
        st.info("Inicia sesión para acceder al sistema.")
        st.stop()
    else:
        st.markdown(f"**Conectado como:** {user.get('username')}")
        if st.button("Cerrar sesión"):
            logout()

# -----------------------------------
# REQUIRE: ahora ya está autenticado
# -----------------------------------
user = get_current_user()
if not user:
    # seguridad extra (esto no debería pasar porque el sidebar ya detuvo)
    st.error("Debes iniciar sesión para continuar.")
    st.stop()

# -----------------------------------
# 1) Comprobación BD (sólo para usuarios autenticados)
# -----------------------------------
st.header("🔍 Comprobación rápida de la base de datos")
if test_connection():
    st.success("Conexión establecida ✅")
else:
    st.error("No se pudo conectar a la base de datos. Revisa Streamlit Secrets.")
    st.stop()

# -----------------------------------
# 2) Mostrar tablas (sólo para usuarios con sesión)
# -----------------------------------
tables = get_table_names() or []
st.write("### Tablas detectadas:")
st.write(", ".join(tables))

st.markdown("---")
st.markdown("Abre las Pages desde el menú lateral `Pages` para ver los CRUDs.")
