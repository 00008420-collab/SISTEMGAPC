# pages/18_caja_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "caja_"
st.set_page_config(layout="wide")
st.title("Caja - CRUD")

rows = run_query("SELECT * FROM caja ORDER BY id_caja DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando caja.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear caja")
    id_ciclo = st.text_input("id_ciclo", key=PREFIX + "id_ciclo")
    id_ahorro = st.text_input("id_ahorro", key=PREFIX + "id_ahorro")
    id_prestamo = st.text_input("id_prestamo", key=PREFIX + "id_prestamo")
    id_pago = st.text_input("id_pago", key=PREFIX + "id_pago")
    saldo_inicial = st.number_input("saldo_inicial", min_value=0.0, format="%.2f", key=PREFIX + "saldo_inicial")
    ingresos = st.number_input("ingresos", min_value=0.0, format="%.2f", key=PREFIX + "ingresos")
    egresos = st.number_input("egresos", min_value=0.0, format="%.2f", key=PREFIX + "egresos")
    saldo_final = st.number_input("saldo_final", min_value=0.0, format="%.2f", key=PREFIX + "saldo_final")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO caja (id_ciclo, id_ahorro, id_prestamo, id_pago, saldo_inicial, ingresos, egresos, saldo_final) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_ciclo or None, id_ahorro or None, id_prestamo or None, id_pago or None, saldo_inicial, ingresos, egresos, saldo_final), fetch=False)
    if ok:
        st.success("Caja creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando caja.")

st.divider()
st.subheader("Editar / Eliminar caja")
id_edit = st.text_input("id_caja a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM caja WHERE id_caja=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            saldo_inicial_e = st.number_input("saldo_inicial", value=rec.get("saldo_inicial") or 0.0, key=PREFIX + "saldo_inicial_e", format="%.2f")
            ingresos_e = st.number_input("ingresos", value=rec.get("ingresos") or 0.0, key=PREFIX + "ingresos_e", format="%.2f")
            egresos_e = st.number_input("egresos", value=rec.get("egresos") or 0.0, key=PREFIX + "egresos_e", format="%.2f")
            saldo_final_e = st.number_input("saldo_final", value=rec.get("saldo_final") or 0.0, key=PREFIX + "saldo_final_e", format="%.2f")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE caja SET saldo_inicial=%s, ingresos=%s, egresos=%s, saldo_final=%s WHERE id_caja=%s;"
            ok = run_query(q, (saldo_inicial_e, ingresos_e, egresos_e, saldo_final_e, id_edit), fetch=False)
            if ok:
                st.success("Caja actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM caja WHERE id_caja=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Caja eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró caja con ese id.")

