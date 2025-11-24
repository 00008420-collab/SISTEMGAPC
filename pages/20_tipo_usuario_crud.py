# pages/20_tipo_usuario_crud.py
import streamlit as st
from db import get_connection

TABLE = "tipo_usuario"
ID_COL = "id_tipo_usuario"

st.title("Tipo de usuario — CRUD")

def list_tipos(limit=200):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_tipo(nombre,apellido,rol):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (nombre,apellido,rol) VALUES (%s,%s,%s)",
                    (nombre,apellido,rol))
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

def update_tipo(pk,nombre,apellido,rol):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET nombre=%s,apellido=%s,rol=%s WHERE `{ID_COL}`=%s",
                    (nombre,apellido,rol,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_tipo(pk):
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
with st.expander("Listar tipos de usuario"):
    if st.button("Cargar tipos"):
        rows=list_tipos()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear tipo de usuario")
with st.form("create_tipo"):
    nombre = st.text_input("nombre")
    apellido = st.text_input("apellido")
    rol = st.text_input("rol")
    if st.form_submit_button("Crear"):
        ok = create_tipo(nombre,apellido,rol)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar tipo"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_tipo"):
                nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                rol = st.text_input("rol", value=str(rec.get("rol") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_tipo(pk,nombre,apellido,rol)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_tipo(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
