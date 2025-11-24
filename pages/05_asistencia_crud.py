# pages/05_asistencia_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "asistencia_"
st.set_page_config(layout="wide")
st.title("Asistencias - CRUD")

rows = run_query("SELECT * FROM asistencia ORDER BY id_asistencia DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando asistencias.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear asistencia")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    id_multa = st.text_input("id_multa", key=PREFIX + "id_multa")
    motivo = st.text_input("motivo", key=PREFIX + "motivo")
    presente_ausente = st.selectbox("presente/ausente", options=["presente","ausente"], key=PREFIX + "presente")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO asistencia (id_miembro, id_multa, motivo, presente_ausente) VALUES (%s,%s,%s,%s);"
    ok = run_query(q, (id_miembro or None, id_multa or None, motivo or None, presente_ausente), fetch=False)
    if ok:
        st.success("Asistencia creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando asistencia.")

st.divider()
st.subheader("Editar / Eliminar asistencia")
id_edit = st.text_input("id_asistencia a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM asistencia WHERE id_asistencia=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_miembro_e = st.text_input("id_miembro", value=rec.get("id_miembro") or "", key=PREFIX + "id_miembro_e")
            id_multa_e = st.text_input("id_multa", value=rec.get("id_multa") or "", key=PREFIX + "id_multa_e")
            motivo_e = st.text_input("motivo", value=rec.get("motivo") or "", key=PREFIX + "motivo_e")
            presente_e = st.selectbox("presente/ausente", options=["presente","ausente"], index=0 if rec.get("presente_ausente")=="presente" else 1, key=PREFIX + "presente_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE asistencia SET id_miembro=%s, id_multa=%s, motivo=%s, presente_ausente=%s WHERE id_asistencia=%s;"
            ok = run_query(q, (id_miembro_e or None, id_multa_e or None, motivo_e or None, presente_e, id_edit), fetch=False)
            if ok:
                st.success("Asistencia actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM asistencia WHERE id_asistencia=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Asistencia eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró asistencia con ese id.")
