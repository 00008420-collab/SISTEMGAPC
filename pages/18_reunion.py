# pages/18_reunion.py
import streamlit as st
from db import run_query

MODULE_KEY = "18_reunion"

def _list_reuniones():
    return run_query("SELECT * FROM reunion ORDER BY id_reunion DESC LIMIT 200;", fetch=True)

def _insert_reunion(id_grupo, id_asistencia, fecha, dia, lugar, tipo):
    q = "INSERT INTO reunion (id_grupo, id_asistencia, fecha, dia, lugar, tipo) VALUES (%s,%s,%s,%s,%s,%s);"
    return run_query(q, (id_grupo, id_asistencia, fecha, dia, lugar, tipo), fetch=False)

def render():
    st.subheader("Reuniones")
    rows = _list_reuniones()
    if rows is None:
        st.error("No se pudieron listar reuniones.")
        return
    st.dataframe(rows)

    st.markdown("---")
    st.markdown("### Agregar reunión")
    with st.form(key=f"{MODULE_KEY}_form"):
        id_grupo = st.text_input("id_grupo", key=f"{MODULE_KEY}_id_grupo")
        id_asistencia = st.text_input("id_asistencia", key=f"{MODULE_KEY}_id_asistencia")
        fecha = st.date_input("fecha", key=f"{MODULE_KEY}_fecha")
        dia = st.text_input("dia", key=f"{MODULE_KEY}_dia")
        lugar = st.text_input("lugar", key=f"{MODULE_KEY}_lugar")
        tipo = st.selectbox("tipo", options=["ordinario","extraordinario"], key=f"{MODULE_KEY}_tipo")
        submitted = st.form_submit_button("Agregar")
    if submitted:
        ok = _insert_reunion(id_grupo, id_asistencia, fecha.strftime("%Y-%m-%d"), dia, lugar, tipo)
        if ok:
            st.success("Reunión agregada.")
            st.experimental_rerun()
        else:
            st.error("Error agregando reunión.")
