# pages/07_prestamo_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

# Verificar inicio de sesión
if "user" not in st.session_state or st.session_state.user is None:
    st.error("Debes iniciar sesión para acceder a esta página.")
    st.stop()

user = st.session_state.user

require_login()
PREFIX = "prestamo_"
st.set_page_config(layout="wide")
st.title("Préstamos — CRUD avanzado")

# Listado
rows = run_query("SELECT * FROM prestamo ORDER BY id_prestamo DESC LIMIT 400;", fetch=True)
if rows is None:
    st.error("Error listando préstamos.")
else:
    st.dataframe(rows)

st.divider()
# Crear/Editar avanzado
with st.form(key=PREFIX + "form"):
    st.subheader("Crear o actualizar préstamo")
    ids = run_query("SELECT id_prestamo FROM prestamo ORDER BY id_prestamo DESC LIMIT 200;", fetch=True) or []
    existing = st.selectbox("Seleccionar préstamo existente (vacío = nuevo)", options=[""] + [r["id_prestamo"] for r in ids], key=PREFIX + "existing")
    id_prestamo = st.text_input("id_prestamo (si vacío se autogenera)", key=PREFIX + "id_prestamo")
    # FK selects (intentar traer nombres si existen)
    id_promotora = st.text_input("id_promotora", key=PREFIX + "id_promotora")
    id_ciclo = st.text_input("id_ciclo", key=PREFIX + "id_ciclo")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    monto = st.number_input("monto", min_value=0.0, format="%.2f", step=1.0, key=PREFIX + "monto")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+500", key=PREFIX + "add500"):
            monto = monto + 500
    with col2:
        if st.button("-500", key=PREFIX + "sub500"):
            monto = max(0, monto - 500)
    intereses = st.slider("intereses (%)", 0.0, 100.0, 5.0, key=PREFIX + "intereses")
    plazo_meses = st.number_input("plazo_meses", min_value=1, max_value=360, value=12, step=1, key=PREFIX + "plazo")
    total_cuotas = int(plazo_meses)
    cuota_estimada = (monto * (1 + intereses/100.0) / plazo_meses) if plazo_meses else 0.0
    st.markdown(f"**Cuota estimada:** {cuota_estimada:.2f} USD / mes — **Total cuotas:** {total_cuotas}")
    saldo_restante = st.number_input("saldo_restante", min_value=0.0, format="%.2f", value=monto, key=PREFIX + "saldo")
    estado = st.selectbox("estado", ["activo","pagado","moroso","cancelado"], index=0, key=PREFIX + "estado")
    submit = st.form_submit_button("Guardar")
if submit:
    if existing:
        q = """UPDATE prestamo SET id_promotora=%s, id_ciclo=%s, id_miembro=%s, monto=%s, intereses=%s, saldo_restante=%s, estado=%s, plazo_meses=%s, total_cuotas=%s
               WHERE id_prestamo=%s;"""
        ok = run_query(q, (id_promotora or None, id_ciclo or None, id_miembro or None, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas, existing), fetch=False)
        if ok:
            st.success("Préstamo actualizado.")
            st.experimental_rerun()
        else:
            st.error("Error actualizando préstamo.")
    else:
        q = """INSERT INTO prestamo (id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        ok = run_query(q, (id_promotora or None, id_ciclo or None, id_miembro or None, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas), fetch=False)
        if ok:
            st.success("Préstamo creado.")
            st.experimental_rerun()
        else:
            st.error("Error creando préstamo.")

st.divider()
# Eliminar
st.subheader("Eliminar préstamo")
id_del = st.text_input("id_prestamo a eliminar", key=PREFIX + "del_id")
if st.button("Eliminar", key=PREFIX + "del_btn"):
    if id_del:
        ok = run_query("DELETE FROM prestamo WHERE id_prestamo=%s;", (id_del,), fetch=False)
        if ok:
            st.success("Préstamo eliminado.")
            st.experimental_rerun()
        else:
            st.error("Error al eliminar.")
    else:
        st.warning("Escribe un id para eliminar.")

