# pages/15_directiva_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "directiva_"
st.set_page_config(layout="wide")
st.title("Directivas - CRUD")

rows = run_query("SELECT * FROM directiva ORDER BY id_directiva DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando directivas.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear directiva")
    id_grupo = st.text_input("id_grupo", key=PREFIX + "id_grupo")
    fecha_inicio = st.date_input("fecha_inicio", key=PREFIX + "fecha_inicio")
    fecha_fin = st.date_input("fecha_fin", key=PREFIX + "fecha_fin")
    activa = st.selectbox("activa/inactiva", options=["activa","inactiva"], key=PREFIX + "activa")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO directiva (id_grupo, fecha_inicio, fecha_fin, activa_inactiva) VALUES (%s,%s,%s,%s);"
    ok = run_query(q, (id_grupo or None, fecha_inicio.isoformat() if hasattr(fecha_inicio,"isoformat") else fecha_inicio, fecha_fin.isoformat() if hasattr(fecha_fin,"isoformat") else fecha_fin, activa), fetch=False)
    if ok:
        st.success("Directiva creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando directiva.")

st.divider()
st.subheader("Editar / Eliminar directiva")
id_edit = st.text_input("id_directiva a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM directiva WHERE id_directiva=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            fecha_inicio_e = st.date_input("fecha_inicio", value=rec.get("fecha_inicio"), key=PREFIX + "fecha_inicio_e")
            fecha_fin_e = st.date_input("fecha_fin", value=rec.get("fecha_fin"), key=PREFIX + "fecha_fin_e")
            activa_e = st.selectbox("activa/inactiva", options=["activa","inactiva"], index=0 if rec.get("activa_inactiva")=="activa" else 1, key=PREFIX + "activa_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE directiva SET fecha_inicio=%s, fecha_fin=%s, activa_inactiva=%s WHERE id_directiva=%s;"
            ok = run_query(q, (fecha_inicio_e.isoformat() if hasattr(fecha_inicio_e,"isoformat") else fecha_inicio_e, fecha_fin_e.isoformat() if hasattr(fecha_fin_e,"isoformat") else fecha_fin_e, activa_e, id_edit), fetch=False)
            if ok:
                st.success("Directiva actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM directiva WHERE id_directiva=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Directiva eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró directiva con ese id.")

