# pages/05_asistencia_crud.py
import streamlit as st
from db import get_connection

TABLE = "asistencia"
ID_COL = "id_asistencia"

st.title("Asistencia — CRUD")

def list_asistencias(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_asistencia(id_miembro,id_multa,motivo,presente):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_miembro,id_multa,motivo,presente) VALUES (%s,%s,%s,%s)",
                    (id_miembro,id_multa,motivo,presente))
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

def update_asistencia(pk,id_miembro,id_multa,motivo,presente):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_miembro=%s,id_multa=%s,motivo=%s,presente=%s WHERE `{ID_COL}`=%s",
                    (id_miembro,id_multa,motivo,presente,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_asistencia(pk):
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
with st.expander("Listar asistencias"):
    if st.button("Cargar asistencias"):
        rows = list_asistencias()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear asistencia")
with st.form("create_asistencia"):
    id_miembro = st.text_input("id_miembro")
    id_multa = st.text_input("id_multa")
    motivo = st.text_input("motivo")
    presente = st.selectbox("presente/ausente", ["presente","ausente"])
    if st.form_submit_button("Crear"):
        ok = create_asistencia(id_miembro,id_multa,motivo,presente)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar asistencia"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_asistencia"):
                id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                id_multa = st.text_input("id_multa", value=str(rec.get("id_multa") or ""))
                motivo = st.text_input("motivo", value=str(rec.get("motivo") or ""))
                presente = st.selectbox("presente/ausente", ["presente","ausente"], index=0 if rec.get("presente")=="presente" else 1)
                if st.form_submit_button("Actualizar"):
                    ok = update_asistencia(pk,id_miembro,id_multa,motivo,presente)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_asistencia(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
