# pages/16_prestamo_crud.py
import streamlit as st
from db import get_connection

TABLE = "prestamo"
ID_COL = "id_prestamo"

st.title("Prestamo — CRUD")

def list_prestamos(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_prestamo(id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas))
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

def update_prestamo(pk,id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_promotora=%s,id_ciclo=%s,id_miembro=%s,monto=%s,intereses=%s,saldo_restante=%s,estado=%s,plazo_meses=%s,total_cuotas=%s WHERE `{ID_COL}`=%s",
                    (id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_prestamo(pk):
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
with st.expander("Listar prestamos"):
    if st.button("Cargar prestamos"):
        rows=list_prestamos()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear prestamo")
with st.form("create_prestamo"):
    id_promotora = st.text_input("id_promotora")
    id_ciclo = st.text_input("id_ciclo")
    id_miembro = st.text_input("id_miembro")
    monto = st.number_input("monto", value=0.0)
    intereses = st.number_input("intereses", value=0.0)
    saldo_restante = st.number_input("saldo_restante", value=0.0)
    estado = st.text_input("estado")
    plazo_meses = st.number_input("plazo_meses", value=1, min_value=1)
    total_cuotas = st.number_input("total_cuotas", value=1, min_value=1)
    if st.form_submit_button("Crear"):
        ok=create_prestamo(id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar prestamo"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
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
                plazo_meses = st.number_input("plazo_meses", value=int(rec.get("plazo_meses") or 1))
                total_cuotas = st.number_input("total_cuotas", value=int(rec.get("total_cuotas") or 1))
                if st.form_submit_button("Actualizar"):
                    ok = update_prestamo(pk,id_promotora,id_ciclo,id_miembro,monto,intereses,saldo_restante,estado,plazo_meses,total_cuotas)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_prestamo(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
