# pages/15_pago_crud.py
import streamlit as st
from db import get_connection

TABLE = "pago"
ID_COL = "id_pago"

st.title("Pago — CRUD")

def list_pagos(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_pago(id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def get_by_id(pk):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        r=cur.fetchone(); cur.close(); return r
    finally:
        conn.close()

def update_pago(pk,id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_prestamo=%s,fecha=%s,monto=%s,interes_pagado=%s,multa_aplicada=%s,saldo_restante=%s,id_cuota=%s WHERE `{ID_COL}`=%s",
                    (id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_pago(pk):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor(); cur.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

# UI
with st.expander("Listar pagos"):
    if st.button("Cargar pagos"):
        rows=list_pagos()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear pago")
with st.form("create_pago"):
    id_prestamo = st.text_input("id_prestamo")
    fecha = st.date_input("fecha")
    monto = st.number_input("monto", value=0.0)
    interes_pagado = st.number_input("interes_pagado", value=0.0)
    multa_aplicada = st.number_input("multa_aplicada", value=0.0)
    saldo_restante = st.number_input("saldo_restante", value=0.0)
    id_cuota = st.text_input("id_cuota")
    if st.form_submit_button("Crear"):
        ok = create_pago(id_prestamo,fecha.isoformat(),monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar pago"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_pago"):
                id_prestamo = st.text_input("id_prestamo", value=str(rec.get("id_prestamo") or ""))
                fecha = st.text_input("fecha", value=str(rec.get("fecha") or ""))
                monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                interes_pagado = st.number_input("interes_pagado", value=float(rec.get("interes_pagado") or 0.0))
                multa_aplicada = st.number_input("multa_aplicada", value=float(rec.get("multa_aplicada") or 0.0))
                saldo_restante = st.number_input("saldo_restante", value=float(rec.get("saldo_restante") or 0.0))
                id_cuota = st.text_input("id_cuota", value=str(rec.get("id_cuota") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_pago(pk,id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_pago(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
