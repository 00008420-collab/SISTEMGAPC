# pages/02_administrador_crud.py
import streamlit as st
from db import get_connection

TABLE = "administrador"
ID_COL = "id_administrador"

st.title("Administrador — CRUD")

def list_admins(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_admin(id_miembro, id_distrito, nombre, apellido, correo, rol):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_miembro`,`id_distrito`,`nombre`,`apellido`,`correo`,`rol`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (id_miembro,id_distrito,nombre,apellido,correo,rol))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar administradores"):
    limit = st.number_input("Límite", min_value=10, max_value=2000, value=200)
    if st.button("Cargar administradores"):
        st.dataframe(list_admins(limit))

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
        ok,msg = create_admin(id_miembro,id_distrito,nombre,apellido,correo,rol)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_administrador")
buscar = st.text_input("id_administrador")
if st.button("Cargar"):
    if not buscar: st.warning("Ingresa id")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s LIMIT 1",(buscar,))
                rec = cur.fetchone()
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
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_miembro`=%s,`id_distrito`=%s,`nombre`=%s,`apellido`=%s,`correo`=%s,`rol`=%s WHERE `{ID_COL}`=%s",
                                             (id_miembro,id_distrito,nombre,apellido,correo,rol,buscar))
                                get_connection().commit()
                            st.success("Actualizado")
                        except Exception as e:
                            st.error(f"Error: {e}")
                if st.button("Eliminar"):
                    try:
                        with get_connection().cursor() as cur3:
                            cur3.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                            get_connection().commit()
                        st.success("Eliminado")
                    except Exception as e:
                        st.error(f"Error: {e}")
