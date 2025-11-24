# pages/16_prestamo_crud.py
import streamlit as st
from db import get_connection

TABLE = "prestamo"
ID_COL = "id_prestamo"

st.title("Préstamo — CRUD")

def list_prestamos(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_prestamo(id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_promotora`,`id_ciclo`,`id_miembro`,`monto`,`intereses`,`saldo_restante`,`estado`,`plazo_meses`,`total_cuotas`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar préstamos"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar préstamos"):
        st.dataframe(list_prestamos(limit))

st.markdown("---")
st.subheader("Crear préstamo")
with st.form("create_prestamo"):
    id_promotora = st.text_input("id_promotora")
    id_ciclo = st.text_input("id_ciclo")
    id_miembro = st.text_input("id_miembro")
    monto = st.number_input("monto", value=0.0)
    intereses = st.number_input("intereses", value=0.0)
    saldo_restante = st.number_input("saldo_restante", value=0.0)
    estado = st.text_input("estado")
    plazo_meses = st.number_input("plazo_meses", value=0, min_value=0)
    total_cuotas = st.number_input("total_cuotas", value=0, min_value=0)
    if st.form_submit_button("Crear"):
        ok,msg = create_prestamo(id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_prestamo")
buscar = st.text_input("id_prestamo")
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
                with st.form("update_prestamo"):
                    id_promotora = st.text_input("id_promotora", value=str(rec.get("id_promotora") or ""))
                    id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                    id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                    monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                    intereses = st.number_input("intereses", value=float(rec.get("intereses") or 0.0))
                    saldo_restante = st.number_input("saldo_restante", value=float(rec.get("saldo_restante") or 0.0))
                    estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                    plazo_meses = st.number_input("plazo_meses", value=int(rec.get("plazo_meses") or 0))
                    total_cuotas = st.number_input("total_cuotas", value=int(rec.get("total_cuotas") or 0))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_promotora`=%s,`id_ciclo`=%s,`id_miembro`=%s,`monto`=%s,`intereses`=%s,`saldo_restante`=%s,`estado`=%s,`plazo_meses`=%s,`total_cuotas`=%s WHERE `{ID_COL}`=%s",
                                             (id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas,buscar))
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
