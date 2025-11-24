import streamlit as st
from auth.login import login_user
from db import test_connection, get_table_names

st.set_page_config(page_title="SGAPC", layout="wide")

# -------------------------------
# 1. Autenticación
# -------------------------------
user = login_user()
if not user:
    st.stop()

st.success(f"Bienvenido, {user['username']}")

# -------------------------------
# 2. Comprobación de BD
# -------------------------------
st.header("🔍 Comprobación rápida de la base de datos")

conn_ok = test_connection()

if conn_ok:
    st.success("Conexión establecida con la base de datos ✔️")
else:
    st.error("❌ No fue posible conectar a la base de datos")
    st.stop()

# Obtener tablas
tables = get_table_names()

if not tables:
    st.warning("No fue posible obtener la lista de tablas.")
else:
    st.write("### Tablas detectadas:")
    st.write(", ".join(tables))

# -------------------------------
# 3. Navegación a CRUDs
# -------------------------------
st.header("📂 Módulos disponibles (CRUDs)")

st.info("Selecciona cualquier página desde el menú lateral izquierdo (Pages).")

