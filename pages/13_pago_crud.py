
# pages/13_pago_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "pago_"
st.set_page_config(layout="wide")
st.title("Pagos - CRUD")

rows = run_query("SELECT * FROM pago ORDER BY id_pago DESC LIMIT 400;", fetch=True)
if rows is None:
    st.error("Error listando pagos.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear pago")
    id_prestamo = st.text_input("id_prestamo", key=PREFIX + "id_prestamo")
    fecha = st.date_input("fecha", key=PREFIX + "fecha")
    monto = st.number_input("monto", min_value=0.0, format="%.2f", key=PREFIX + "monto")
    interes_pagado = st.number_input("interes_pagado", min_value=0.0, format="%.2f", key=PREFIX + "interes_pagado")
    multa_aplicada = st.number_input("multa_aplicada", min_value=0.0, format="%.2f", key=PREFIX + "multa_aplicada")
    saldo_restante = st.number_input("saldo_restante", min_value=0.0, format="%.2f", key=PREFIX + "saldo_restante")
    id_cuota = st.text_input("id_cuota", key=PREFIX + "id_cuota")
    submit = st.form_submit_button("Crear")
if submit:
    q = "INSERT INTO pago (id_prestamo, fecha, monto, interes_pagado, multa_aplicada, saldo_restante, id_cuota) VALUES (%s,%s,%s,%s,%s,%s,%s);"
    ok = run_query(q, (id_prestamo or None, fecha.isoformat() if hasattr(fecha,"isoformat") else fecha, monto, interes_pagado, multa_aplicada, saldo_restante, id_cuota or None), fetch=False)
    if ok:
        st.success("Pago creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando pago.")

st.divider()
st.subheader("Editar / Eliminar pago")
id_edit = st.text_input("id_pago a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM pago WHERE id_pago=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            id_prestamo_e = st.text_input("id_prestamo", value=rec.get("id_prestamo") or "", key=PREFIX + "id_prestamo_e")
            fecha_e = st.date_input("fecha", value=rec.get("fecha"), key=PREFIX + "fecha_e")
            monto_e = st.number_input("monto", value=rec.get("monto") or 0.0, key=PREFIX + "monto_e", format="%.2f")
            interes_e = st.number_input("interes_pagado", value=rec.get("interes_pagado") or 0.0, key=PREFIX + "interes_e", format="%.2f")
            multa_e = st.number_input("multa_aplicada", value=rec.get("multa_aplicada") or 0.0, key=PREFIX + "multa_e", format="%.2f")
            saldo_e = st.number_input("saldo_restante", value=rec.get("saldo_restante") or 0.0, key=PREFIX + "saldo_e", format="%.2f")
            id_cuota_e = st.text_input("id_cuota", value=rec.get("id_cuota") or "", key=PREFIX + "id_cuota_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE pago SET id_prestamo=%s, fecha=%s, monto=%s, interes_pagado=%s, multa_aplicada=%s, saldo_restante=%s, id_cuota=%s WHERE id_pago=%s;"
            ok = run_query(q, (id_prestamo_e or None, fecha_e.isoformat() if hasattr(fecha_e,"isoformat") else fecha_e, monto_e, interes_e, multa_e, saldo_e, id_cuota_e or None, id_edit), fetch=False)
            if ok:
                st.success("Pago actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM pago WHERE id_pago=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Pago eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró pago con ese id.")
