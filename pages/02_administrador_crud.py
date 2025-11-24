# pages/02_administrador_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "administrador_"
st.set_page_config(layout="wide")
st.title("Administrador - CRUD")

# Listado
rows = run_query("SELECT * FROM administrador ORDER BY id_administrador DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando administradores.")
else:
    st.dataframe(rows)

st.divider()
# Crear
with st.form(key=PREFIX + "create"):
    st.subheader("Crear administrador")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    id_distrito = st.text_input("id_distrito", key=PREFIX + "id_distrito")
    nombre = st.text_input("nombre", key=PREFIX + "nombre")
    apellido = st.text_input("apellido", key=PREFIX + "apellido")
    correo = st.text_input("correo", key=PREFIX + "correo")
    rol = st.text_input("rol", key=PREFIX + "rol")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO administrador (id_miembro, id_distrito, nombre, apellido, correo, rol) VALUES (%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_miembro or None, id_distrito or None, nombre or None, apellido or None, correo or None, rol or None), fetch=False)
    if ok:
        st.success("Administrador creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando administrador.")

st.divider()
# Editar / Eliminar
st.subheader("Editar / Eliminar administrador")
id_edit = st.text_input("id_administrador a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM administrador WHERE id_administrador=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_miembro_e = st.text_input("id_miembro", value=rec.get("id_miembro") or "", key=PREFIX + "id_miembro_e")
            id_distrito_e = st.text_input("id_distrito", value=rec.get("id_distrito") or "", key=PREFIX + "id_distrito_e")
            nombre_e = st.text_input("nombre", value=rec.get("nombre") or "", key=PREFIX + "nombre_e")
            apellido_e = st.text_input("apellido", value=rec.get("apellido") or "", key=PREFIX + "apellido_e")
            correo_e = st.text_input("correo", value=rec.get("correo") or "", key=PREFIX + "correo_e")
            rol_e = st.text_input("rol", value=rec.get("rol") or "", key=PREFIX + "rol_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE administrador SET id_miembro=%s, id_distrito=%s, nombre=%s, apellido=%s, correo=%s, rol=%s WHERE id_administrador=%s;"
            ok = run_query(q, (id_miembro_e or None, id_distrito_e or None, nombre_e or None, apellido_e or None, correo_e or None, rol_e or None, id_edit), fetch=False)
            if ok:
                st.success("Administrador actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM administrador WHERE id_administrador=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Administrador eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró administrador con ese id.")
