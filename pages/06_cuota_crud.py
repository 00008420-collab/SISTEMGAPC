# pages/06_cuota_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "cuota_"
st.set_page_config(layout="wide")
st.title("Cuotas - CRUD")

rows = run_query("SELECT * FROM cuota ORDER BY id_cuota DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando cuotas.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear cuota")
    id_prestamo = st.text_input("id_prestamo", key=PREFIX + "id_prestamo")
    fecha_venc = st.date_input("fecha_de_vencimiento", key=PREFIX + "fecha_venc")
    numero = st.number_input("numero", min_value=0, step=1, key=PREFIX + "numero")
    monto_capital = st.number_input("monto_capital", min_value=0.0, format="%.2f", key=PREFIX + "monto_capital")
    monto_interes = st.number_input("monto_interes", min_value=0.0, format="%.2f", key=PREFIX + "monto_interes")
    monto_total = st.number_input("monto_total", min_value=0.0, format="%.2f", key=PREFIX + "monto_total")
    estado = st.text_input("estado", key=PREFIX + "estado")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO cuota (id_prestamo, fecha_de_vencimiento, numero, monto_capital, monto_interes, monto_total, estado) VALUES (%s,%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_prestamo or None, fecha_venc.isoformat() if hasattr(fecha_venc,"isoformat") else fecha_venc, numero, monto_capital, monto_interes, monto_total, estado or None), fetch=False)
    if ok:
        st.success("Cuota creada.")
        st.experimental_rerun()
    else:
        st.error("Error creando cuota.")

st.divider()
st.subheader("Editar / Eliminar cuota")
id_edit = st.text_input("id_cuota a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM cuota WHERE id_cuota=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_prestamo_e = st.text_input("id_prestamo", value=rec.get("id_prestamo") or "", key=PREFIX + "id_prestamo_e")
            fecha_venc_e = st.date_input("fecha_de_vencimiento", value=rec.get("fecha_de_vencimiento"), key=PREFIX + "fecha_venc_e")
            numero_e = st.number_input("numero", value=rec.get("numero") or 0, key=PREFIX + "numero_e", step=1)
            monto_capital_e = st.number_input("monto_capital", value=rec.get("monto_capital") or 0.0, key=PREFIX + "monto_capital_e", format="%.2f")
            monto_interes_e = st.number_input("monto_interes", value=rec.get("monto_interes") or 0.0, key=PREFIX + "monto_interes_e", format="%.2f")
            monto_total_e = st.number_input("monto_total", value=rec.get("monto_total") or 0.0, key=PREFIX + "monto_total_e", format="%.2f")
            estado_e = st.text_input("estado", value=rec.get("estado") or "", key=PREFIX + "estado_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE cuota SET id_prestamo=%s, fecha_de_vencimiento=%s, numero=%s, monto_capital=%s, monto_interes=%s, monto_total=%s, estado=%s WHERE id_cuota=%s;"
            ok = run_query(q, (id_prestamo_e or None, fecha_venc_e.isoformat() if hasattr(fecha_venc_e,"isoformat") else fecha_venc_e, numero_e, monto_capital_e, monto_interes_e, monto_total_e, estado_e or None, id_edit), fetch=False)
            if ok:
                st.success("Cuota actualizada.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM cuota WHERE id_cuota=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Cuota eliminada.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró cuota con ese id.")
