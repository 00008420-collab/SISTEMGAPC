# pages/11_distrito_crud.py
import streamlit as st
from db import get_connection

TABLE = "distrito"
ID_COL = "id_distrito"

st.title("Distrito — CRUD")

def list_distritos(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_distrito(id_grupo,nombre,lugar):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_grupo,nombre,lugar) VALUES (%s,%s,%s)",
                    (id_grupo,nombre,lugar))
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

def update_distrito(pk,id_grupo,nombre,lugar):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_grupo=%s,nombre=%s,lugar=%s WHERE `{ID_COL}`=%s",
                    (id_grupo,nombre,lugar,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_distrito(pk):
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
with st.expander("Listar distritos"):
    if st.button("Cargar distritos"):
        rows=list_distritos()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear distrito")
with st.form("create_distrito"):
    id_grupo = st.text_input("id_grupo")
    nombre = st.text_input("nombre")
    lugar = st.text_input("lugar")
    if st.form_submit_button("Crear"):
        ok = create_distrito(id_grupo,nombre,lugar)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar distrito"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_distrito"):
                id_grupo = st.text_input("id_grupo", value=str(rec.get("id_grupo") or ""))
                nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                lugar = st.text_input("lugar", value=str(rec.get("lugar") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_distrito(pk,id_grupo,nombre,lugar)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_distrito(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
