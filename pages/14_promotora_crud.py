# pages/14_promotora_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "promotora_"
st.set_page_config(layout="wide")
st.title("Promotoras - CRUD")

rows = run_query("SELECT * FROM promotora ORDER BY id_promotora DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando promotoras.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear promotora")
    id_administrador = st.text_input("id_administrador", key=PREFIX + "id_administrador")
    nombre = st.text_input("nombre", key=PREFIX + "nombre")
    apellido = st.text_input("apellido", key=PREFIX + "apellido")
    telefono = st.text_input("telefono", key=PREFIX + "telefono")
    correo = st.text_input("correo", key=PREFIX + "correo")
    distrito = st.text_input("distrito", key=PREFIX + "distrito")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO promotora (id_administrador, nombre, apellido, telefono, correo, distrito) VALUES (%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_administrador or None, nombre or None, apellido or None, telefono or None, correo or None, distrito or None), fetch=False)
    if ok:
        st.success("Promotora creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando promotora.")

st.divider()
st.subheader("Editar / Eliminar promotora")
id_edit = st.text_input("id_promotora a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM promotora WHERE id_promotora=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_administrador_e = st.text_input("id_administrador", value=rec.get("id_administrador") or "", key=PREFIX + "id_administrador_e")
            nombre_e = st.text_input("nombre", value=rec.get("nombre") or "", key=PREFIX + "nombre_e")
            apellido_e = st.text_input("apellido", value=rec.get("apellido") or "", key=PREFIX + "apellido_e")
            telefono_e = st.text_input("telefono", value=rec.get("telefono") or "", key=PREFIX + "telefono_e")
            correo_e = st.text_input("correo", value=rec.get("correo") or "", key=PREFIX + "correo_e")
            distrito_e = st.text_input("distrito", value=rec.get("distrito") or "", key=PREFIX + "distrito_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE promotora SET id_administrador=%s, nombre=%s, apellido=%s, telefono=%s, correo=%s, distrito=%s WHERE id_promotora=%s;"
            ok = run_query(q, (id_administrador_e or None, nombre_e or None, apellido_e or None, telefono_e or None, correo_e or None, distrito_e or None, id_edit), fetch=False)
            if ok:
                st.success("Promotora actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM promotora WHERE id_promotora=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Promotora eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró promotora con ese id.")
