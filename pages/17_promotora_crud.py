# pages/17_promotora_crud.py
import streamlit as st
from db import get_connection

TABLE = "promotora"
ID_COL = "id_promotora"

st.title("Promotora — CRUD")

def list_promotoras(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_promotora(id_administrador,nombre,apellido,telefono,correo,distrito):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_administrador,nombre,apellido,telefono,correo,distrito) VALUES (%s,%s,%s,%s,%s,%s)",
                    (id_administrador,nombre,apellido,telefono,correo,distrito))
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

def update_promotora(pk,id_administrador,nombre,apellido,telefono,correo,distrito):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_administrador=%s,nombre=%s,apellido=%s,telefono=%s,correo=%s,distrito=%s WHERE `{ID_COL}`=%s",
                    (id_administrador,nombre,apellido,telefono,correo,distrito,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_promotora(pk):
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
with st.expander("Listar promotoras"):
    if st.button("Cargar promotoras"):
        rows=list_promotoras()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear promotora")
with st.form("create_promotora"):
    id_administrador = st.text_input("id_administrador")
    nombre = st.text_input("nombre")
    apellido = st.text_input("apellido")
    telefono = st.text_input("telefono")
    correo = st.text_input("correo")
    distrito = st.text_input("distrito")
    if st.form_submit_button("Crear"):
        ok=create_promotora(id_administrador,nombre,apellido,telefono,correo,distrito)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar promotora"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_promotora"):
                id_administrador = st.text_input("id_administrador", value=str(rec.get("id_administrador") or ""))
                nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                telefono = st.text_input("telefono", value=str(rec.get("telefono") or ""))
                correo = st.text_input("correo", value=str(rec.get("correo") or ""))
                distrito = st.text_input("distrito", value=str(rec.get("distrito") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_promotora(pk,id_administrador,nombre,apellido,telefono,correo,distrito)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_promotora(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
