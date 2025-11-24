
# pages/17_reporte_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "reporte_"
st.set_page_config(layout="wide")
st.title("Reportes - CRUD")

rows = run_query("SELECT * FROM reporte ORDER BY id_reporte DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando reportes.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear reporte")
    id_ciclo = st.text_input("id_ciclo", key=PREFIX + "id_ciclo")
    id_administrador = st.text_input("id_administrador", key=PREFIX + "id_administrador")
    fecha_generacion = st.date_input("fecha_de_generacion", key=PREFIX + "fecha")
    tipo = st.text_input("tipo", key=PREFIX + "tipo")
    descripcion = st.text_area("descripcion", key=PREFIX + "descripcion")
    estado = st.text_input("estado", key=PREFIX + "estado")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO reporte (id_ciclo, id_administrador, fecha_de_generacion, tipo, descripcion, estado) VALUES (%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_ciclo or None, id_administrador or None, fecha_generacion.isoformat() if hasattr(fecha_generacion,"isoformat") else fecha_generacion, tipo or None, descripcion or None, estado or None), fetch=False)
    if ok:
        st.success("Reporte creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando reporte.")

st.divider()
st.subheader("Editar / Eliminar reporte")
id_edit = st.text_input("id_reporte a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM reporte WHERE id_reporte=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            tipo_e = st.text_input("tipo", value=rec.get("tipo") or "", key=PREFIX + "tipo_e")
            descripcion_e = st.text_area("descripcion", value=rec.get("descripcion") or "", key=PREFIX + "descripcion_e")
            estado_e = st.text_input("estado", value=rec.get("estado") or "", key=PREFIX + "estado_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE reporte SET tipo=%s, descripcion=%s, estado=%s WHERE id_reporte=%s;"
            ok = run_query(q, (tipo_e or None, descripcion_e or None, estado_e or None, id_edit), fetch=False)
            if ok:
                st.success("Reporte actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM reporte WHERE id_reporte=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Reporte eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró reporte con ese id.")
