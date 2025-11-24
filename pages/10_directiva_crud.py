# pages/10_directiva_crud.py
import streamlit as st
from db import get_connection

TABLE = "directiva"
ID_COL = "id_directiva"

st.title("Directiva — CRUD")

def list_directivas(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_directiva(id_grupo,fecha_inicio,fecha_fin,activa):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_grupo,fecha_inicio,fecha_fin,activa) VALUES (%s,%s,%s,%s)",
                    (id_grupo,fecha_inicio,fecha_fin,activa))
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

def update_directiva(pk,id_grupo,fecha_inicio,fecha_fin,activa):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_grupo=%s,fecha_inicio=%s,fecha_fin=%s,activa=%s WHERE `{ID_COL}`=%s",
                    (id_grupo,fecha_inicio,fecha_fin,activa,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_directiva(pk):
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
with st.expander("Listar directivas"):
    if st.button("Cargar directivas"):
        rows=list_directivas()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear directiva")
with st.form("create_directiva"):
    id_grupo = st.text_input("id_grupo")
    fecha_inicio = st.date_input("fecha_inicio")
    fecha_fin = st.date_input("fecha_fin")
    activa = st.selectbox("activa/inactiva", ["activa","inactiva"])
    if st.form_submit_button("Crear"):
        ok = create_directiva(id_grupo,fecha_inicio.isoformat(),fecha_fin.isoformat(),activa)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar directiva"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_directiva"):
                id_grupo = st.text_input("id_grupo", value=str(rec.get("id_grupo") or ""))
                fecha_inicio = st.text_input("fecha_inicio", value=str(rec.get("fecha_inicio") or ""))
                fecha_fin = st.text_input("fecha_fin", value=str(rec.get("fecha_fin") or ""))
                activa = st.selectbox("activa/inactiva", ["activa","inactiva"], index=0 if rec.get("activa")=="activa" else 1)
                if st.form_submit_button("Actualizar"):
                    ok = update_directiva(pk,id_grupo,fecha_inicio,fecha_fin,activa)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_directiva(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
