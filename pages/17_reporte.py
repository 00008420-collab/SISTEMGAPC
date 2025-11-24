# pages/17_reporte.py
import streamlit as st
from db import run_query

MODULE_KEY = "17_reporte"

def _list_reportes():
    return run_query("SELECT * FROM reporte ORDER BY id_reporte DESC LIMIT 200;", fetch=True)

def _insert_reporte(id_ciclo, id_administrador, fecha_generacion, tipo, descripcion, estado):
    q = "INSERT INTO reporte (id_ciclo, id_administrador, fecha_de_generacion, tipo, descripcion, estado) VALUES (%s,%s,%s,%s,%s,%s);"
    return run_query(q, (id_ciclo, id_administrador, fecha_generacion, tipo, descripcion, estado), fetch=False)

def render():
    st.subheader("Reportes")
    rows = _list_reportes()
    if rows is None:
        st.error("No se pudieron listar reportes.")
        return
    st.dataframe(rows)

    st.markdown("---")
    st.markdown("### Generar reporte")
    with st.form(key=f"{MODULE_KEY}_form"):
        id_ciclo = st.text_input("id_ciclo", key=f"{MODULE_KEY}_id_ciclo")
        id_administrador = st.text_input("id_administrador", key=f"{MODULE_KEY}_id_administrador")
        fecha_generacion = st.date_input("fecha_de_generacion", key=f"{MODULE_KEY}_fecha_generacion")
        tipo = st.text_input("tipo", key=f"{MODULE_KEY}_tipo")
        descripcion = st.text_area("descripcion", key=f"{MODULE_KEY}_descripcion")
        estado = st.selectbox("estado", options=["borrador","finalizado"], key=f"{MODULE_KEY}_estado")
        submitted = st.form_submit_button("Generar")
    if submitted:
        ok = _insert_reporte(id_ciclo, id_administrador, fecha_generacion.strftime("%Y-%m-%d"), tipo, descripcion, estado)
        if ok:
            st.success("Reporte generado.")
            st.experimental_rerun()
        else:
            st.error("Error generando reporte.")
