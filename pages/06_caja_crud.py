# pages/06_caja_crud.py
import streamlit as st
from db import get_connection

TABLE = "caja"
ID_COL = "id_caja"

st.title("Caja — CRUD")

def list_cajas(limit=200):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_caja(id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final))
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

def update_caja(pk,id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_ciclo=%s,id_ahorro=%s,id_prestamo=%s,id_pago=%s,saldo_inicial=%s,ingresos=%s,egresos=%s,saldo_final=%s WHERE `{ID_COL}`=%s",
                    (id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_caja(pk):
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
with st.expander("Listar cajas"):
    if st.button("Cargar cajas"):
        rows=list_cajas()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

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
        ok=create_caja(id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar caja"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
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
                    ok = update_caja(pk,id_ciclo,id_ahorro,id_prestamo,id_pago,saldo_inicial,ingresos,egresos,saldo_final)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_caja(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
