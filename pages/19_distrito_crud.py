# pages/19_distrito_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "distrito_"
st.set_page_config(layout="wide")
st.title("Distritos - CRUD")

rows = run_query("SELECT * FROM distrito ORDER BY id_distrito DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando distritos.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear distrito")
    id_grupo = st.text_input("id_grupo", key=PREFIX + "id_grupo")
    nombre = st.text_input("nombre", key=PREFIX + "nombre")
    lugar = st.text_input("lugar", key=PREFIX + "lugar")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO distrito (id_grupo, nombre, lugar) VALUES (%s,%s,%s);"
    ok = run_query(q, (id_grupo or None, nombre or None, lugar or None), fetch=False)
    if ok:
        st.success("Distrito creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando distrito.")

st.divider()
st.subheader("Editar / Eliminar distrito")
id_edit = st.text_input("id_distrito a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM distrito WHERE id_distrito=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_grupo_e = st.text_input("id_grupo", value=rec.get("id_grupo") or "", key=PREFIX + "id_grupo_e")
            nombre_e = st.text_input("nombre", value=rec.get("nombre") or "", key=PREFIX + "nombre_e")
            lugar_e = st.text_input("lugar", value=rec.get("lugar") or "", key=PREFIX + "lugar_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE distrito SET id_grupo=%s, nombre=%s, lugar=%s WHERE id_distrito=%s;"
            ok = run_query(q, (id_grupo_e or None, nombre_e or None, lugar_e or None, id_edit), fetch=False)
            if ok:
                st.success("Distrito actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM distrito WHERE id_distrito=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Distrito eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró distrito con ese id.")

