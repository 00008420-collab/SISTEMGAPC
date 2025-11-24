# pages/16_ciclo_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "ciclo_"
st.set_page_config(layout="wide")
st.title("Ciclos - CRUD")

rows = run_query("SELECT * FROM ciclo ORDER BY id_ciclo DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando ciclos.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear ciclo")
    fecha_inicio = st.date_input("fecha_inicio", key=PREFIX + "fecha_inicio")
    fecha_fin = st.date_input("fecha_fin", key=PREFIX + "fecha_fin")
    estado = st.text_input("estado", key=PREFIX + "estado")
    total_utilidad = st.number_input("total_utilidad", min_value=0.0, format="%.2f", key=PREFIX + "total_utilidad")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO ciclo (fecha_inicio, fecha_fin, estado, total_utilidad) VALUES (%s,%s,%s,%s);"
    ok = run_query(q, (fecha_inicio.isoformat() if hasattr(fecha_inicio,"isoformat") else fecha_inicio, fecha_fin.isoformat() if hasattr(fecha_fin,"isoformat") else fecha_fin, estado or None, total_utilidad), fetch=False)
    if ok:
        st.success("Ciclo creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando ciclo.")

st.divider()
st.subheader("Editar / Eliminar ciclo")
id_edit = st.text_input("id_ciclo a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM ciclo WHERE id_ciclo=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            fecha_inicio_e = st.date_input("fecha_inicio", value=rec.get("fecha_inicio"), key=PREFIX + "fecha_inicio_e")
            fecha_fin_e = st.date_input("fecha_fin", value=rec.get("fecha_fin"), key=PREFIX + "fecha_fin_e")
            estado_e = st.text_input("estado", value=rec.get("estado") or "", key=PREFIX + "estado_e")
            total_utilidad_e = st.number_input("total_utilidad", value=rec.get("total_utilidad") or 0.0, key=PREFIX + "total_utilidad_e", format="%.2f")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE ciclo SET fecha_inicio=%s, fecha_fin=%s, estado=%s, total_utilidad=%s WHERE id_ciclo=%s;"
            ok = run_query(q, (fecha_inicio_e.isoformat() if hasattr(fecha_inicio_e,"isoformat") else fecha_inicio_e, fecha_fin_e.isoformat() if hasattr(fecha_fin_e,"isoformat") else fecha_fin_e, estado_e or None, total_utilidad_e, id_edit), fetch=False)
            if ok:
                st.success("Ciclo actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM ciclo WHERE id_ciclo=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Ciclo eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró ciclo con ese id.")

