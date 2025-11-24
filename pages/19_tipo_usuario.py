# pages/19_tipo_usuario.py
import streamlit as st
from db import run_query

MODULE_KEY = "19_tipo_usuario"

def _list_tipos():
    return run_query("SELECT * FROM tipo_usuario ORDER BY id_tipo DESC LIMIT 200;", fetch=True)

def _insert_tipo(nombre, apellido, rol):
    q = "INSERT INTO tipo_usuario (nombre, apellido, rol) VALUES (%s,%s,%s);"
    return run_query(q, (nombre, apellido, rol), fetch=False)

def render():
    st.subheader("Tipos de usuario")
    rows = _list_tipos()
    if rows is None:
        st.error("No se pudieron listar tipos de usuario.")
        return
    st.dataframe(rows)

    st.markdown("---")
    st.markdown("### Nuevo tipo de usuario")
    with st.form(key=f"{MODULE_KEY}_form"):
        nombre = st.text_input("nombre", key=f"{MODULE_KEY}_nombre")
        apellido = st.text_input("apellido", key=f"{MODULE_KEY}_apellido")
        rol = st.text_input("rol", key=f"{MODULE_KEY}_rol")
        submitted = st.form_submit_button("Crear tipo")
    if submitted:
        ok = _insert_tipo(nombre, apellido, rol)
        if ok:
            st.success("Tipo creado.")
            st.experimental_rerun()
        else:
            st.error("Error creando tipo.")
