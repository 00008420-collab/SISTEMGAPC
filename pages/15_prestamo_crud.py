# pages/15_prestamo_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

PAGE_KEY = "prestamo_crud"

# Requerir login (detendrá la app si no está autenticado)
user = require_login()

st.set_page_config(page_title="Prestamos - CRUD", page_icon="🏦", layout="wide")

st.title("Préstamos — CRUD avanzado")
st.write("Control y gestión de préstamos. Usa el formulario para crear, editar o eliminar préstamos.")

# --- util: traer lista de ids existentes ---
def get_prestamo_ids():
    rows = run_query("SELECT id_prestamo FROM prestamo ORDER BY id_prestamo ASC")
    if not rows:
        return []
    return [r["id_prestamo"] for r in rows]

# --- util: traer datos de un id ---
def load_prestamo(id_prestamo):
    r = run_query("SELECT * FROM prestamo WHERE id_prestamo=%s LIMIT 1", (id_prestamo,))
    return r[0] if r else None

# --- util: crear/actualizar/eliminar ---
def crear_prestamo(data: dict):
    q = """
    INSERT INTO prestamo (id_prestamo, id_promotora, id_ciclo, id_miembro, monto, intereses,
                         saldo_restante, estado, plazo_meses, total_cuotas)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    params = (
        data["id_prestamo"],
        data["id_promotora"],
        data["id_ciclo"],
        data["id_miembro"],
        data["monto"],
        data["intereses"],
        data["saldo_restante"],
        data["estado"],
        data["plazo_meses"],
        data["total_cuotas"],
    )
    return run_query(q, params, fetch=False)

def actualizar_prestamo(data: dict):
    q = """
    UPDATE prestamo SET id_promotora=%s, id_ciclo=%s, id_miembro=%s, monto=%s, intereses=%s,
                       saldo_restante=%s, estado=%s, plazo_meses=%s, total_cuotas=%s
    WHERE id_prestamo=%s
    """
    params = (
        data["id_promotora"],
        data["id_ciclo"],
        data["id_miembro"],
        data["monto"],
        data["intereses"],
        data["saldo_restante"],
        data["estado"],
        data["plazo_meses"],
        data["total_cuotas"],
        data["id_prestamo"],
    )
    return run_query(q, params, fetch=False)

def eliminar_prestamo(id_prestamo):
    return run_query("DELETE FROM prestamo WHERE id_prestamo=%s", (id_prestamo,), fetch=False)

# ---------- UI ----------
ids = get_prestamo_ids()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Seleccionar préstamo existente")
    selected = st.selectbox("ID préstamo (selecciona para editar)", options=["-- nuevo --"] + ids, key=PAGE_KEY + "_select_id")

    st.markdown("---")
    st.write("Opciones rápidas")
    if st.button("Recargar lista de préstamos", key=PAGE_KEY + "_reload"):
        st.experimental_rerun()

with col2:
    # Si seleccionó uno existente, cargar datos
    data = {
        "id_prestamo": "",
        "id_promotora": "",
        "id_ciclo": "",
        "id_miembro": "",
        "monto": 0.0,
        "intereses": 0.0,
        "saldo_restante": 0.0,
        "estado": "activo",
        "plazo_meses": 1,
        "total_cuotas": 1,
    }

    if selected and selected != "-- nuevo --":
        row = load_prestamo(selected)
        if row:
            data.update({
                "id_prestamo": row.get("id_prestamo"),
                "id_promotora": row.get("id_promotora"),
                "id_ciclo": row.get("id_ciclo"),
                "id_miembro": row.get("id_miembro"),
                "monto": float(row.get("monto") or 0),
                "intereses": float(row.get("intereses") or 0),
                "saldo_restante": float(row.get("saldo_restante") or 0),
                "estado": row.get("estado") or "activo",
                "plazo_meses": int(row.get("plazo_meses") or 1),
                "total_cuotas": int(row.get("total_cuotas") or 1),
            })

    st.subheader("Formulario de préstamo")
    # usar form para evitar múltiples re-ejecuciones y claves únicas
    with st.form(key=PAGE_KEY + "_form"):
        id_prestamo = st.text_input("ID préstamo", value=str(data["id_prestamo"]) if data["id_prestamo"] else "", key=PAGE_KEY + "_id")
        # Para los FK: idealmente obtener listas reales; aquí usamos text_inputs/selectboxes simples
        id_promotora = st.text_input("ID promotora", value=str(data["id_promotora"]) if data["id_promotora"] else "", key=PAGE_KEY + "_promotora")
        id_ciclo = st.text_input("ID ciclo", value=str(data["id_ciclo"]) if data["id_ciclo"] else "", key=PAGE_KEY + "_ciclo")
        id_miembro = st.text_input("ID miembro", value=str(data["id_miembro"]) if data["id_miembro"] else "", key=PAGE_KEY + "_miembro")

        st.markdown("**Montos y condiciones**")
        monto = st.number_input("Monto (USD)", value=float(data["monto"]), min_value=0.0, format="%.2f", step=1.0, key=PAGE_KEY + "_monto")
        intereses = st.slider("Interés (%)", min_value=0, max_value=100, value=int(data["intereses"]), key=PAGE_KEY + "_interes")
        plazo_meses = st.number_input("Plazo (meses)", min_value=1, max_value=360, value=int(data["plazo_meses"]), step=1, key=PAGE_KEY + "_plazo")
        # calculos automáticos
        total_with_interest = monto * (1 + (intereses / 100.0))
        cuota_mensual = (total_with_interest / plazo_meses) if plazo_meses else total_with_interest
        total_cuotas = int(plazo_meses)

        st.markdown(f"**Cuota mensual estimada:** `{cuota_mensual:.2f}` — **Total pagado (estimado):** `{total_with_interest:.2f}`")

        # saldo restante y estado
        saldo_restante = st.number_input("Saldo restante", value=float(data["saldo_restante"]), min_value=0.0, format="%.2f", step=1.0, key=PAGE_KEY + "_saldo")
        estado = st.selectbox("Estado", options=["activo", "pagado", "moroso", "cancelado"], index=["activo","pagado","moroso","cancelado"].index(data["estado"]) if data["estado"] in ["activo","pagado","moroso","cancelado"] else 0, key=PAGE_KEY + "_estado")

        # botones
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            submit_create = st.form_submit_button("Crear préstamo", use_container_width=True, key=PAGE_KEY + "_btn_create")
        with col_b:
            submit_update = st.form_submit_button("Actualizar préstamo", use_container_width=True, key=PAGE_KEY + "_btn_update")
        with col_c:
            submit_delete = st.form_submit_button("Eliminar préstamo", use_container_width=True, key=PAGE_KEY + "_btn_delete")

    # procesar botones
    if submit_create:
        if not id_prestamo:
            st.error("Debe indicar un id_prestamo para crear.")
        else:
            payload = {
                "id_prestamo": id_prestamo,
                "id_promotora": id_promotora or None,
                "id_ciclo": id_ciclo or None,
                "id_miembro": id_miembro or None,
                "monto": monto,
                "intereses": intereses,
                "saldo_restante": saldo_restante if saldo_restante>0 else monto,
                "estado": estado,
                "plazo_meses": int(plazo_meses),
                "total_cuotas": total_cuotas,
            }
            ok = crear_prestamo(payload)
            if ok:
                st.success("Préstamo creado correctamente.")
                st.experimental_rerun()
            else:
                st.error("Error creando préstamo. Revisa logs o claves duplicadas.")

    if submit_update:
        if not id_prestamo:
            st.error("Seleccione / indique un id_prestamo para actualizar.")
        else:
            payload = {
                "id_prestamo": id_prestamo,
                "id_promotora": id_promotora or None,
                "id_ciclo": id_ciclo or None,
                "id_miembro": id_miembro or None,
                "monto": monto,
                "intereses": intereses,
                "saldo_restante": saldo_restante,
                "estado": estado,
                "plazo_meses": int(plazo_meses),
                "total_cuotas": total_cuotas,
            }
            ok = actualizar_prestamo(payload)
            if ok:
                st.success("Préstamo actualizado correctamente.")
                st.experimental_rerun()
            else:
                st.error("No se pudo actualizar. Revisa que el id exista.")

    if submit_delete:
        if not id_prestamo:
            st.error("Selecciona un id para eliminar.")
        else:
            confirm = st.confirm("¿Estás segura/o? Esta acción eliminará el préstamo.", key=PAGE_KEY + "_confirm_delete")
            if confirm:
                ok = eliminar_prestamo(id_prestamo)
                if ok:
                    st.success("Préstamo eliminado.")
                    st.experimental_rerun()
                else:
                    st.error("No se pudo eliminar. Revisa dependencias o permisos.")
