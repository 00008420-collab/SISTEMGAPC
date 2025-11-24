# pages/13_miembro_crud.py
import streamlit as st
from db import get_connection

TABLE = "miembro"
ID_COL = "id_miembro"

st.title("Miembro — CRUD")

def list_miembros(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_miembro(id_tipo_usuario,apellido,dui,direccion):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_tipo_usuario,apellido,dui,direccion) VALUES (%s,%s,%s,%s)",
                    (id_tipo_usuario,apellido,dui,direccion))
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

def update_miembro(pk,id_tipo_usuario,apellido,dui,direccion):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_tipo_usuario=%s,apellido=%s,dui=%s,direccion=%s WHERE `{ID_COL}`=%s",
                    (id_tipo_usuario,apellido,dui,direccion,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_miembro(pk):
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
with st.expander("Listar miembros"):
    if st.button("Cargar miembros"):
        rows=list_miembros()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear miembro")
with st.form("create_miembro"):
    id_tipo_usuario = st.text_input("id_tipo_usuario")
    apellido = st.text_input("apellido")
    dui = st.text_input("dui")
    direccion = st.text_input("direccion")
    if st.form_submit_button("Crear"):
        ok=create_miembro(id_tipo_usuario,apellido,dui,direccion)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar miembro"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_miembro"):
                id_tipo_usuario = st.text_input("id_tipo_usuario", value=str(rec.get("id_tipo_usuario") or ""))
                apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                dui = st.text_input("dui", value=str(rec.get("dui") or ""))
                direccion = st.text_input("direccion", value=str(rec.get("direccion") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_miembro(pk,id_tipo_usuario,apellido,dui,direccion)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_miembro(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
