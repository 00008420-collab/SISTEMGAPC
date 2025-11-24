# pages/09_miembro_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "miembro_"
st.set_page_config(layout="wide")
st.title("Miembros - CRUD")

rows = run_query("SELECT * FROM miembro ORDER BY id_miembro DESC LIMIT 400;", fetch=True)
if rows is None:
    st.error("Error listando miembros.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear miembro")
    id_tipo_usuario = st.text_input("id_tipo_usuario", key=PREFIX + "id_tipo_usuario")
    apellido = st.text_input("apellido", key=PREFIX + "apellido")
    dui = st.text_input("dui", key=PREFIX + "dui")
    direccion = st.text_input("direccion", key=PREFIX + "direccion")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO miembro (id_tipo_usuario, apellido, dui, direccion) VALUES (%s,%s,%s,%s);"
    ok = run_query(q, (id_tipo_usuario or None, apellido or None, dui or None, direccion or None), fetch=False)
    if ok:
        st.success("Miembro creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando miembro.")

st.divider()
st.subheader("Editar / Eliminar miembro")
id_edit = st.text_input("id_miembro a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM miembro WHERE id_miembro=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_tipo_usuario_e = st.text_input("id_tipo_usuario", value=rec.get("id_tipo_usuario") or "", key=PREFIX + "id_tipo_usuario_e")
            apellido_e = st.text_input("apellido", value=rec.get("apellido") or "", key=PREFIX + "apellido_e")
            dui_e = st.text_input("dui", value=rec.get("dui") or "", key=PREFIX + "dui_e")
            direccion_e = st.text_input("direccion", value=rec.get("direccion") or "", key=PREFIX + "direccion_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE miembro SET id_tipo_usuario=%s, apellido=%s, dui=%s, direccion=%s WHERE id_miembro=%s;"
            ok = run_query(q, (id_tipo_usuario_e or None, apellido_e or None, dui_e or None, direccion_e or None, id_edit), fetch=False)
            if ok:
                st.success("Miembro actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM miembro WHERE id_miembro=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Miembro eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró miembro con ese id.")

