# pages/11_tipo_usuario_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "tipo_usuario_"
st.set_page_config(layout="wide")
st.title("Tipo de Usuario - CRUD")

rows = run_query("SELECT * FROM tipo_usuario ORDER BY id_tipo_usuario DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando tipos de usuario.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear tipo de usuario")
    nombre = st.text_input("nombre", key=PREFIX + "nombre")
    apellido = st.text_input("apellido", key=PREFIX + "apellido")
    rol = st.text_input("rol", key=PREFIX + "rol")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO tipo_usuario (nombre, apellido, rol) VALUES (%s,%s,%s);"
    ok = run_query(q, (nombre or None, apellido or None, rol or None), fetch=False)
    if ok:
        st.success("Tipo de usuario creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando tipo de usuario.")

st.divider()
st.subheader("Editar / Eliminar tipo de usuario")
id_edit = st.text_input("id_tipo_usuario a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM tipo_usuario WHERE id_tipo_usuario=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            nombre_e = st.text_input("nombre", value=rec.get("nombre") or "", key=PREFIX + "nombre_e")
            apellido_e = st.text_input("apellido", value=rec.get("apellido") or "", key=PREFIX + "apellido_e")
            rol_e = st.text_input("rol", value=rec.get("rol") or "", key=PREFIX + "rol_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE tipo_usuario SET nombre=%s, apellido=%s, rol=%s WHERE id_tipo_usuario=%s;"
            ok = run_query(q, (nombre_e or None, apellido_e or None, rol_e or None, id_edit), fetch=False)
            if ok:
                st.success("Tipo de usuario actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM tipo_usuario WHERE id_tipo_usuario=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Tipo de usuario eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró tipo de usuario con ese id.")
