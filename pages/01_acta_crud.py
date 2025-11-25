# pages/01_acta_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

# Verificar inicio de sesión
if "user" not in st.session_state or st.session_state.user is None:
    st.error("Debes iniciar sesión para acceder a esta página.")
    st.stop()

user = st.session_state.user

require_login()
PREFIX = "acta_"
st.set_page_config(layout="wide")
st.title("Actas - CRUD")

# Listado
st.subheader("Listado de actas")
rows = run_query("SELECT * FROM acta ORDER BY id_acta DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando actas.")
else:
    st.dataframe(rows)

st.divider()
# Crear
with st.form(key=PREFIX + "create"):
    st.subheader("Crear acta")
    id_ciclo = st.text_input("id_ciclo", key=PREFIX + "id_ciclo")
    tipo = st.text_input("tipo", key=PREFIX + "tipo")
    fecha = st.date_input("fecha", key=PREFIX + "fecha")
    descripcion = st.text_area("descripcion", key=PREFIX + "descripcion")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO acta (id_ciclo, tipo, fecha, descripcion) VALUES (%s,%s,%s,%s);"
    ok = run_query(q, (id_ciclo or None, tipo or None, fecha.isoformat() if hasattr(fecha,"isoformat") else fecha, descripcion or None), fetch=False)
    if ok:
        st.success("Acta creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando acta.")

st.divider()
# Editar / Eliminar
st.subheader("Editar / Eliminar acta")
id_edit = st.text_input("id_acta a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM acta WHERE id_acta=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_ciclo_e = st.text_input("id_ciclo", value=rec.get("id_ciclo") or "", key=PREFIX + "id_ciclo_e")
            tipo_e = st.text_input("tipo", value=rec.get("tipo") or "", key=PREFIX + "tipo_e")
            fecha_e = st.date_input("fecha", value=rec.get("fecha"), key=PREFIX + "fecha_e")
            descripcion_e = st.text_area("descripcion", value=rec.get("descripcion") or "", key=PREFIX + "descripcion_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE acta SET id_ciclo=%s, tipo=%s, fecha=%s, descripcion=%s WHERE id_acta=%s;"
            ok = run_query(q, (id_ciclo_e or None, tipo_e or None, fecha_e.isoformat() if hasattr(fecha_e,"isoformat") else fecha_e, descripcion_e or None, id_edit), fetch=False)
            if ok:
                st.success("Acta actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM acta WHERE id_acta=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Acta eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró acta con ese id.")
