# app.py
import streamlit as st
from auth.login import login_user
from auth.config import check_login
from db import get_connection, get_table_names

st.set_page_config(page_title="SGAPC - Menú", layout="wide")

# inicializar estado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Si no está logueado, muestra el formulario de login (en el sidebar)
if not st.session_state.logged_in:
    login_user()
    st.stop()

# si llega aquí, ya está logueado
check_login()

st.title("📘 SGAPC - Menú")
st.write("Bienvenido al sistema. Usa el menú izquierdo (o Pages) para abrir los CRUDs.")

# --- Centro: comprobación rápida de la DB ---
st.header("Comprobación rápida de la base de datos")

conn = get_connection()
if conn:
    st.success("Conectado a la base de datos ✅")
    # mostrar lista de tablas
    tablas = get_table_names()
    if tablas:
        st.write("Tablas detectadas:")
        st.write(", ".join(tablas))
    else:
        st.info("No se detectaron tablas (o la consulta devolvió vacío).")
    try:
        conn.close()
    except Exception:
        pass
else:
    st.error("No se pudo conectar a la base de datos. Revisa los secrets y credenciales.")
