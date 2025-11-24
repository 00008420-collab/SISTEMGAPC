# pages/15_pago_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "pago"
ID_COL = "id_pago"

st.title("Pago — CRUD")

def list_pagos(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_pago(id_prestamo, fecha, monto, interes_pagado, multa_aplicada, saldo_restante, id_cuota):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_prestamo`,`fecha`,`monto`,`interes_pagado`,`multa_aplicada`,`saldo_restante`,`id_cuota`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (id_prestamo,fecha,monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar pagos"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar pagos"):
        st.dataframe(list_pagos(limit))

st.markdown("---")
st.subheader("Crear pago")
with st.form("create_pago"):
    id_prestamo = st.text_input("id_prestamo")
    fecha = st.date_input("fecha", value=date.today())
    monto = st.number_input("monto", value=0.0)
    interes_pagado = st.number_input("interes_pagado", value=0.0)
    multa_aplicada = st.number_input("multa_aplicada", value=0.0)
    saldo_restante = st.number_input("saldo_restante", value=0.0)
    id_cuota = st.text_input("id_cuota")
    if st.form_submit_button("Crear"):
        ok,msg = create_pago(id_prestamo,fecha.isoformat(),monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_pago")
buscar = st.text_input("id_pago")
if st.button("Cargar"):
    if not buscar: st.warning("Ingresa id")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                rec = cur.fetchone()
            if not rec: st.info("No encontrado")
            else:
                st.json(rec)
                with st.form("update_pago"):
                    id_prestamo = st.text_input("id_prestamo", value=str(rec.get("id_prestamo") or ""))
                    try:
                        fecha_in = date.fromisoformat(str(rec.get("fecha")))
                    except Exception:
                        fecha_in = date.today()
                    fecha_in = st.date_input("fecha", value=fecha_in)
                    monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                    interes_pagado = st.number_input("interes_pagado", value=float(rec.get("interes_pagado") or 0.0))
                    multa_aplicada = st.number_input("multa_aplicada", value=float(rec.get("multa_aplicada") or 0.0))
                    saldo_restante = st.number_input("saldo_restante", value=float(rec.get("saldo_restante") or 0.0))
                    id_cuota = st.text_input("id_cuota", value=str(rec.get("id_cuota") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_prestamo`=%s,`fecha`=%s,`monto`=%s,`interes_pagado`=%s,`multa_aplicada`=%s,`saldo_restante`=%s,`id_cuota`=%s WHERE `{ID_COL}`=%s",
                                             (id_prestamo,fecha_in.isoformat(),monto,interes_pagado,multa_aplicada,saldo_restante,id_cuota,buscar))
                                get_connection().commit()
                            st.success("Actualizado")
                        except Exception as e:
                            st.error(f"Error: {e}")
                if st.button("Eliminar"):
                    try:
                        with get_connection().cursor() as cur3:
                            cur3.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                            get_connection().commit()
                        st.success("Eliminado")
                    except Exception as e:
                        st.error(f"Error: {e}")
