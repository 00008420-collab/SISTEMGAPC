# pages/02_administrador_crud.py
import streamlit as st
from db import get_connection

TABLE = "administrador"
ID_COL = "id_administrador"

st.title("Administrador — CRUD")

def list_admin(limit=200):
    conn = get_connection(); 
    if not conn: return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows = cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_admin(id_miembro,id_distrito,nombre,apellido,correo,rol):
    conn = get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_miembro,id_distrito,nombre,apellido,correo,rol) VALUES (%s,%s,%s,%s,%s,%s)",
                    (id_miembro,id_distrito,nombre,apellido,correo,rol))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def get_by_id(pk):
    conn = get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        r=cur.fetchone(); cur.close(); return r
    finally:
        conn.close()

def update_admin(pk,id_miembro,id_distrito,nombre,apellido,correo,rol):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_miembro=%s,id_distrito=%s,nombre=%s,apellido=%s,correo=%s,rol=%s WHERE `{ID_COL}`=%s",
                    (id_miembro,id_distrito,nombre,apellido,correo,rol,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_admin(pk):
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
with st.expander("Listar administradores"):
    limit = st.number_input("Límite", value=200, min_value=1, key="adm_lim")
    if st.button("Cargar administradores"):
        rows = list_admin(limit)
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear administrador")
with st.form("create_admin"):
    id_miembro = st.text_input("id_miembro")
    id_distrito = st.text_input("id_distrito")
    nombre = st.text_input("nombre")
    apellido = st.text_input("apellido")
    correo = st.text_input("correo")
    rol = st.text_input("rol")
    if st.form_submit_button("Crear"):
        ok = create_admin(id_miembro,id_distrito,nombre,apellido,correo,rol)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL, key="adm_pk")
if st.button("Cargar admin"):
    if not pk: st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_admin"):
                id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                id_distrito = st.text_input("id_distrito", value=str(rec.get("id_distrito") or ""))
                nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                correo = st.text_input("correo", value=str(rec.get("correo") or ""))
                rol = st.text_input("rol", value=str(rec.get("rol") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_admin(pk,id_miembro,id_distrito,nombre,apellido,correo,rol)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar admin"):
                ok = delete_admin(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
