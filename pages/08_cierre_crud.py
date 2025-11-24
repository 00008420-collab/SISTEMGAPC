# pages/08_cierre_crud.py
import streamlit as st
from db import get_connection

TABLE = "cierre"
ID_COL = "id_cierre"

st.title("Cierre — CRUD")

def list_cierres(limit=200):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_cierre(id_ciclo,descripcion,fecha):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_ciclo,descripcion,fecha) VALUES (%s,%s,%s)",
                    (id_ciclo,descripcion,fecha))
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

def update_cierre(pk,id_ciclo,descripcion,fecha):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_ciclo=%s,descripcion=%s,fecha=%s WHERE `{ID_COL}`=%s",
                    (id_ciclo,descripcion,fecha,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_cierre(pk):
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
with st.expander("Listar cierres"):
    if st.button("Cargar cierres"):
        rows=list_cierres()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear cierre")
with st.form("create_cierre"):
    id_ciclo = st.text_input("id_ciclo")
    descripcion = st.text_area("descripcion")
    fecha = st.date_input("fecha")
    if st.form_submit_button("Crear"):
        ok = create_cierre(id_ciclo,descripcion,fecha.isoformat())
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar cierre"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_cierre"):
                id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                fecha = st.text_input("fecha", value=str(rec.get("fecha") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_cierre(pk,id_ciclo,descripcion,fecha)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_cierre(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
