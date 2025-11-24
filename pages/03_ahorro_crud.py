# pages/03_ahorro_crud.py
import streamlit as st
from db import get_connection

TABLE = "ahorro"
ID_COL = "id_ahorro"

st.title("Ahorro — CRUD")

def list_ahorros(limit=200):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_ahorro(id_miembro,monto_actual,saldo_actual,fecha_actualizacion):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_miembro,monto_actual,saldo_actual,fecha_actualizacion) VALUES (%s,%s,%s,%s)",
                    (id_miembro,monto_actual,saldo_actual,fecha_actualizacion))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def get_by_id(pk):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        r=cur.fetchone(); cur.close(); return r
    finally:
        conn.close()

def update_ahorro(pk,id_miembro,monto_actual,saldo_actual,fecha_actualizacion):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_miembro=%s,monto_actual=%s,saldo_actual=%s,fecha_actualizacion=%s WHERE `{ID_COL}`=%s",
                    (id_miembro,monto_actual,saldo_actual,fecha_actualizacion,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_ahorro(pk):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor(); cur.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

# UI
with st.expander("Listar ahorros"):
    if st.button("Cargar ahorros"):
        rows = list_ahorros()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear ahorro")
with st.form("create_ahorro"):
    id_miembro = st.text_input("id_miembro")
    monto_actual = st.number_input("monto_actual", value=0.0, format="%f")
    saldo_actual = st.number_input("saldo_actual", value=0.0, format="%f")
    fecha_actualizacion = st.date_input("fecha_actualizacion")
    if st.form_submit_button("Crear"):
        ok = create_ahorro(id_miembro,monto_actual,saldo_actual,fecha_actualizacion.isoformat())
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar ahorro"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_ahorro"):
                id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                monto_actual = st.number_input("monto_actual", value=float(rec.get("monto_actual") or 0.0))
                saldo_actual = st.number_input("saldo_actual", value=float(rec.get("saldo_actual") or 0.0))
                fecha_actualizacion = st.text_input("fecha_actualizacion", value=str(rec.get("fecha_actualizacion") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_ahorro(pk,id_miembro,monto_actual,saldo_actual,fecha_actualizacion)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_ahorro(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
