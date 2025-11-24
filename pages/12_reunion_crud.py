# pages/12_reunion_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "reunion_"
st.set_page_config(layout="wide")
st.title("Reuniones - CRUD")

rows = run_query("SELECT * FROM reunion ORDER BY id_reunion DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando reuniones.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear reunión")
    id_grupo = st.text_input("id_grupo", key=PREFIX + "id_grupo")
    id_asistencia = st.text_input("id_asistencia", key=PREFIX + "id_asistencia")
    fecha = st.date_input("fecha", key=PREFIX + "fecha")
    dia = st.text_input("dia", key=PREFIX + "dia")
    lugar = st.text_input("lugar", key=PREFIX + "lugar")
    tipo = st.selectbox("extraordinario/ordinario", options=["ordinario","extraordinario"], key=PREFIX + "tipo")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO reunion (id_grupo, id_asistencia, fecha, dia, lugar, tipo) VALUES (%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_grupo or None, id_asistencia or None, fecha.isoformat() if hasattr(fecha,"isoformat") else fecha, dia or None, lugar or None, tipo), fetch=False)
    if ok:
        st.success("Reunión creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando reunión.")

st.divider()
st.subheader("Editar / Eliminar reunión")
id_edit = st.text_input("id_reunion a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM reunion WHERE id_reunion=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_grupo_e = st.text_input("id_grupo", value=rec.get("id_grupo") or "", key=PREFIX + "id_grupo_e")
            id_asistencia_e = st.text_input("id_asistencia", value=rec.get("id_asistencia") or "", key=PREFIX + "id_asistencia_e")
            fecha_e = st.date_input("fecha", value=rec.get("fecha"), key=PREFIX + "fecha_e")
            dia_e = st.text_input("dia", value=rec.get("dia") or "", key=PREFIX + "dia_e")
            lugar_e = st.text_input("lugar", value=rec.get("lugar") or "", key=PREFIX + "lugar_e")
            tipo_e = st.selectbox("extraordinario/ordinario", options=["ordinario","extraordinario"], index=0 if rec.get("tipo")=="ordinario" else 1, key=PREFIX + "tipo_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE reunion SET id_grupo=%s, id_asistencia=%s, fecha=%s, dia=%s, lugar=%s, tipo=%s WHERE id_reunion=%s;"
            ok = run_query(q, (id_grupo_e or None, id_asistencia_e or None, fecha_e.isoformat() if hasattr(fecha_e,"isoformat") else fecha_e, dia_e or None, lugar_e or None, tipo_e, id_edit), fetch=False)
            if ok:
                st.success("Reunión actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM reunion WHERE id_reunion=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Reunión eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró reunión con ese id.")

