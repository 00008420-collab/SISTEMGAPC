# pages/04_aporte_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "aporte_"
st.set_page_config(layout="wide")
st.title("Aportes - CRUD")

rows = run_query("SELECT * FROM aporte ORDER BY id_aporte DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando aportes.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear aporte")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    id_reunion = st.text_input("id_reunion", key=PREFIX + "id_reunion")
    monto = st.number_input("monto", min_value=0.0, format="%.2f", key=PREFIX + "monto")
    fecha = st.date_input("fecha", key=PREFIX + "fecha")
    tipo = st.text_input("tipo", key=PREFIX + "tipo")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO aporte (id_miembro, id_reunion, monto, fecha, tipo) VALUES (%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_miembro or None, id_reunion or None, monto, fecha.isoformat() if hasattr(fecha,"isoformat") else fecha, tipo or None), fetch=False)
    if ok:
        st.success("Aporte creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando aporte.")

st.divider()
st.subheader("Editar / Eliminar aporte")
id_edit = st.text_input("id_aporte a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM aporte WHERE id_aporte=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_miembro_e = st.text_input("id_miembro", value=rec.get("id_miembro") or "", key=PREFIX + "id_miembro_e")
            id_reunion_e = st.text_input("id_reunion", value=rec.get("id_reunion") or "", key=PREFIX + "id_reunion_e")
            monto_e = st.number_input("monto", value=rec.get("monto") or 0.0, key=PREFIX + "monto_e", format="%.2f")
            fecha_e = st.date_input("fecha", value=rec.get("fecha"), key=PREFIX + "fecha_e")
            tipo_e = st.text_input("tipo", value=rec.get("tipo") or "", key=PREFIX + "tipo_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE aporte SET id_miembro=%s, id_reunion=%s, monto=%s, fecha=%s, tipo=%s WHERE id_aporte=%s;"
            ok = run_query(q, (id_miembro_e or None, id_reunion_e or None, monto_e, fecha_e.isoformat() if hasattr(fecha_e,"isoformat") else fecha_e, tipo_e or None, id_edit), fetch=False)
            if ok:
                st.success("Aporte actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM aporte WHERE id_aporte=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Aporte eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró aporte con ese id.")
