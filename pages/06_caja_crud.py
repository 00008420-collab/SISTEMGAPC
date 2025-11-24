# pages/06_caja_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "caja"
ID_COL = "id_caja"

st.title("Caja — CRUD")

def list_cajas(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_caja(id_ciclo, id_ahorro, id_prestamo, id_pago, saldo_inicial, ingresos, egresos, saldo_final):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_ciclo`,`id_ahorro`,`id_prestamo`,`id_pago`,`saldo_inicial`,`ingresos`,`egresos`,`saldo_final`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        (id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar cajas"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar cajas"):
        st.dataframe(list_cajas(limit))

st.markdown("---")
st.subheader("Crear caja")
with st.form("create_caja"):
    id_ciclo = st.text_input("id_ciclo")
    id_ahorro = st.text_input("id_ahorro")
    id_prestamo = st.text_input("id_prestamo")
    id_pago = st.text_input("id_pago")
    saldo_inicial = st.number_input("saldo_inicial", value=0.0)
    ingresos = st.number_input("ingresos", value=0.0)
    egresos = st.number_input("egresos", value=0.0)
    saldo_final = st.number_input("saldo_final", value=0.0)
    if st.form_submit_button("Crear"):
        ok,msg = create_caja(id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_caja")
buscar = st.text_input("id_caja")
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
                with st.form("update_caja"):
                    id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                    id_ahorro = st.text_input("id_ahorro", value=str(rec.get("id_ahorro") or ""))
                    id_prestamo = st.text_input("id_prestamo", value=str(rec.get("id_prestamo") or ""))
                    id_pago = st.text_input("id_pago", value=str(rec.get("id_pago") or ""))
                    saldo_inicial = st.number_input("saldo_inicial", value=float(rec.get("saldo_inicial") or 0.0))
                    ingresos = st.number_input("ingresos", value=float(rec.get("ingresos") or 0.0))
                    egresos = st.number_input("egresos", value=float(rec.get("egresos") or 0.0))
                    saldo_final = st.number_input("saldo_final", value=float(rec.get("saldo_final") or 0.0))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_ciclo`=%s,`id_ahorro`=%s,`id_prestamo`=%s,`id_pago`=%s,`saldo_inicial`=%s,`ingresos`=%s,`egresos`=%s,`saldo_final`=%s WHERE `{ID_COL}`=%s",
                                             (id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final,buscar))
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
