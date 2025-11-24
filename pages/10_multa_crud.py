# pages/10_multa_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "multa_"
st.set_page_config(layout="wide")
st.title("Multas - CRUD")

rows = run_query("SELECT * FROM multa ORDER BY id_multa DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando multas.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear multa")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    tipo = st.text_input("tipo", key=PREFIX + "tipo")
    monto = st.number_input("monto", min_value=0.0, format="%.2f", key=PREFIX + "monto")
    descripcion = st.text_area("descripcion", key=PREFIX + "descripcion")
    fecha = st.date_input("fecha", key=PREFIX + "fecha")
    estado = st.text_input("estado", key=PREFIX + "estado")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO multa (id_miembro, tipo, monto, descripcion, fecha, estado) VALUES (%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_miembro or None, tipo or None, monto, descripcion or None, fecha.isoformat() if hasattr(fecha,"isoformat") else fecha, estado or None), fetch=False)
    if ok:
        st.success("Multa creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando multa.")

st.divider()
st.subheader("Editar / Eliminar multa")
id_edit = st.text_input("id_multa a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM multa WHERE id_multa=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_miembro_e = st.text_input("id_miembro", value=rec.get("id_miembro") or "", key=PREFIX + "id_miembro_e")
            tipo_e = st.text_input("tipo", value=rec.get("tipo") or "", key=PREFIX + "tipo_e")
            monto_e = st.number_input("monto", value=rec.get("monto") or 0.0, key=PREFIX + "monto_e", format="%.2f")
            descripcion_e = st.text_area("descripcion", value=rec.get("descripcion") or "", key=PREFIX + "descripcion_e")
            fecha_e = st.date_input("fecha", value=rec.get("fecha"), key=PREFIX + "fecha_e")
            estado_e = st.text_input("estado", value=rec.get("estado") or "", key=PREFIX + "estado_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE multa SET id_miembro=%s, tipo=%s, monto=%s, descripcion=%s, fecha=%s, estado=%s WHERE id_multa=%s;"
            ok = run_query(q, (id_miembro_e or None, tipo_e or None, monto_e, descripcion_e or None, fecha_e.isoformat() if hasattr(fecha_e,"isoformat") else fecha_e, estado_e or None, id_edit), fetch=False)
            if ok:
                st.success("Multa actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM multa WHERE id_multa=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Multa eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró multa con ese id.")
