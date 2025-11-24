# pages/04_aporte_crud.py
import streamlit as st
from db import get_connection

TABLE = "aporte"
ID_COL = "id_aporte"

st.title("Aporte — CRUD")

def list_aportes(limit=200):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_aporte(id_miembro,id_reunion,monto,fecha,tipo):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_miembro,id_reunion,monto,fecha,tipo) VALUES (%s,%s,%s,%s,%s)",
                    (id_miembro,id_reunion,monto,fecha,tipo))
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

def update_aporte(pk,id_miembro,id_reunion,monto,fecha,tipo):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_miembro=%s,id_reunion=%s,monto=%s,fecha=%s,tipo=%s WHERE `{ID_COL}`=%s",
                    (id_miembro,id_reunion,monto,fecha,tipo,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_aporte(pk):
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
with st.expander("Listar aportes"):
    if st.button("Cargar aportes"):
        rows = list_aportes()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear aporte")
with st.form("create_aporte"):
    id_miembro = st.text_input("id_miembro")
    id_reunion = st.text_input("id_reunion")
    monto = st.number_input("monto", value=0.0)
    fecha = st.date_input("fecha")
    tipo = st.text_input("tipo")
    if st.form_submit_button("Crear"):
        ok = create_aporte(id_miembro,id_reunion,monto,fecha.isoformat(),tipo)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar aporte"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_aporte"):
                id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                id_reunion = st.text_input("id_reunion", value=str(rec.get("id_reunion") or ""))
                monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                fecha = st.text_input("fecha", value=str(rec.get("fecha") or ""))
                tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_aporte(pk,id_miembro,id_reunion,monto,fecha,tipo)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_aporte(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
