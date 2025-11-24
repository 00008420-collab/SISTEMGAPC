# pages/07_ciclo_crud.py
import streamlit as st
from db import get_connection

TABLE = "ciclo"
ID_COL = "id_ciclo"

st.title("Ciclo — CRUD")

def list_ciclos(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_ciclo(fecha_inicio,fecha_fin,estado,total_utilidad):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (fecha_inicio,fecha_fin,estado,total_utilidad) VALUES (%s,%s,%s,%s)",
                    (fecha_inicio,fecha_fin,estado,total_utilidad))
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

def update_ciclo(pk,fecha_inicio,fecha_fin,estado,total_utilidad):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET fecha_inicio=%s,fecha_fin=%s,estado=%s,total_utilidad=%s WHERE `{ID_COL}`=%s",
                    (fecha_inicio,fecha_fin,estado,total_utilidad,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_ciclo(pk):
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
with st.expander("Listar ciclos"):
    if st.button("Cargar ciclos"):
        rows = list_ciclos()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear ciclo")
with st.form("create_ciclo"):
    fecha_inicio = st.date_input("fecha_inicio")
    fecha_fin = st.date_input("fecha_fin")
    estado = st.text_input("estado")
    total_utilidad = st.number_input("total_utilidad", value=0.0)
    if st.form_submit_button("Crear"):
        ok = create_ciclo(fecha_inicio.isoformat(),fecha_fin.isoformat(),estado,total_utilidad)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar ciclo"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_ciclo"):
                fecha_inicio = st.text_input("fecha_inicio", value=str(rec.get("fecha_inicio") or ""))
                fecha_fin = st.text_input("fecha_fin", value=str(rec.get("fecha_fin") or ""))
                estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                total_utilidad = st.number_input("total_utilidad", value=float(rec.get("total_utilidad") or 0.0))
                if st.form_submit_button("Actualizar"):
                    ok = update_ciclo(pk,fecha_inicio,fecha_fin,estado,total_utilidad)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_ciclo(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
