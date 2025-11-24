# pages/16_promotora.py
import streamlit as st
from db import run_query

MODULE_KEY = "16_promotora"

def _list_promotoras():
    return run_query("SELECT * FROM promotora ORDER BY id_promotora DESC LIMIT 200;", fetch=True)

def _insert_promotora(id_administrador, nombre, apellido, telefono, correo, distrito):
    q = "INSERT INTO promotora (id_administrador, nombre, apellido, telefono, correo, distrito) VALUES (%s,%s,%s,%s,%s,%s);"
    return run_query(q, (id_administrador, nombre, apellido, telefono, correo, distrito), fetch=False)

def render():
    st.subheader("Promotoras")
    rows = _list_promotoras()
    if rows is None:
        st.error("No se pudieron listar promotoras.")
        return
    st.dataframe(rows)

    st.markdown("---")
    st.markdown("### Nueva promotora")
    with st.form(key=f"{MODULE_KEY}_form"):
        id_administrador = st.text_input("id_administrador", key=f"{MODULE_KEY}_id_administrador")
        nombre = st.text_input("nombre", key=f"{MODULE_KEY}_nombre")
        apellido = st.text_input("apellido", key=f"{MODULE_KEY}_apellido")
        telefono = st.text_input("telefono", key=f"{MODULE_KEY}_telefono")
        correo = st.text_input("correo", key=f"{MODULE_KEY}_correo")
        distrito = st.text_input("distrito", key=f"{MODULE_KEY}_distrito")
        submitted = st.form_submit_button("Crear promotora")
    if submitted:
        ok = _insert_promotora(id_administrador, nombre, apellido, telefono, correo, distrito)
        if ok:
            st.success("Promotora creada.")
            st.experimental_rerun()
        else:
            st.error("Error creando promotora.")
