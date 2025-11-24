# pages/03_ahorro_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "ahorro_"
st.set_page_config(layout="wide")
st.title("Ahorros - CRUD")

rows = run_query("SELECT * FROM ahorro ORDER BY id_ahorro DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando ahorros.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear ahorro")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    monto_actual = st.number_input("monto_actual", min_value=0.0, format="%.2f", key=PREFIX + "monto_actual")
    saldo_actual = st.number_input("saldo_actual", min_value=0.0, format="%.2f", key=PREFIX + "saldo_actual")
    fecha_actualizacion = st.date_input("fecha_de_actualizacion", key=PREFIX + "fecha_actualizacion")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO ahorro (id_miembro, monto_actual, saldo_actual, fecha_de_actualizacion) VALUES (%s,%s,%s,%s);"
    ok = run_query(q, (id_miembro or None, monto_actual, saldo_actual, fecha_actualizacion.isoformat() if hasattr(fecha_actualizacion,"isoformat") else fecha_actualizacion), fetch=False)
    if ok:
        st.success("Ahorro creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando ahorro.")

st.divider()
st.subheader("Editar / Eliminar ahorro")
id_edit = st.text_input("id_ahorro a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM ahorro WHERE id_ahorro=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_miembro_e = st.text_input("id_miembro", value=rec.get("id_miembro") or "", key=PREFIX + "id_miembro_e")
            monto_actual_e = st.number_input("monto_actual", value=rec.get("monto_actual") or 0.0, key=PREFIX + "monto_actual_e", format="%.2f")
            saldo_actual_e = st.number_input("saldo_actual", value=rec.get("saldo_actual") or 0.0, key=PREFIX + "saldo_actual_e", format="%.2f")
            fecha_actualizacion_e = st.date_input("fecha_de_actualizacion", value=rec.get("fecha_de_actualizacion"), key=PREFIX + "fecha_actualizacion_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE ahorro SET id_miembro=%s, monto_actual=%s, saldo_actual=%s, fecha_de_actualizacion=%s WHERE id_ahorro=%s;"
            ok = run_query(q, (id_miembro_e or None, monto_actual_e, saldo_actual_e, fecha_actualizacion_e.isoformat() if hasattr(fecha_actualizacion_e,"isoformat") else fecha_actualizacion_e, id_edit), fetch=False)
            if ok:
                st.success("Ahorro actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM ahorro WHERE id_ahorro=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Ahorro eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró ahorro con ese id.")
