# pages/15_prestamo.py
import streamlit as st
from db import run_query

MODULE_KEY = "15_prestamo"

def _list_prestamos():
    return run_query("SELECT * FROM prestamo ORDER BY id_prestamo DESC LIMIT 200;", fetch=True)

def _get_existing_ids():
    rows = run_query("SELECT id_prestamo FROM prestamo ORDER BY id_prestamo;", fetch=True)
    if not rows:
        return []
    return [r["id_prestamo"] for r in rows]

def _insert_prestamo(id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas):
    q = """INSERT INTO prestamo (id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    return run_query(q, (id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas), fetch=False)

def render():
    st.subheader("Préstamos")
    rows = _list_prestamos()
    if rows is None:
        st.error("No se pudieron listar préstamos.")
        return
    st.dataframe(rows)

    st.markdown("---")
    st.markdown("### Nuevo préstamo (UI asistida)")
    existing = _get_existing_ids()
    st.info("Si existe id, selecciona una existente; si no, deja vacío para crear uno nuevo.")
    with st.form(key=f"{MODULE_KEY}_form"):
        id_promotora = st.text_input("id_promotora", key=f"{MODULE_KEY}_id_promotora")
        id_ciclo = st.text_input("id_ciclo", key=f"{MODULE_KEY}_id_ciclo")
        id_miembro = st.text_input("id_miembro", key=f"{MODULE_KEY}_id_miembro")
        # si hay ids existentes, mostrar selectbox desplegable opcional
        if existing:
            chosen = st.selectbox("IDs existentes (opcional)", options=[""] + existing, key=f"{MODULE_KEY}_existing_id")
        monto = st.number_input("Monto", min_value=0.0, value=0.0, step=50.0, key=f"{MODULE_KEY}_monto")
        intereses = st.slider("Interés (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1, key=f"{MODULE_KEY}_intereses")
        saldo_restante = st.number_input("Saldo restante", min_value=0.0, value=0.0, key=f"{MODULE_KEY}_saldo_restante")
        estado = st.selectbox("Estado", options=["activo","pagado","mora"], key=f"{MODULE_KEY}_estado")
        plazo_meses = st.number_input("Plazo (meses)", min_value=1, value=6, key=f"{MODULE_KEY}_plazo_meses")
        total_cuotas = st.number_input("Total cuotas", min_value=1, value=int(plazo_meses), key=f"{MODULE_KEY}_total_cuotas")
        submitted = st.form_submit_button("Crear préstamo")
    if submitted:
        ok = _insert_prestamo(id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, int(plazo_meses), int(total_cuotas))
        if ok:
            st.success("Préstamo creado.")
            st.experimental_rerun()
        else:
            st.error("Error creando préstamo.")
