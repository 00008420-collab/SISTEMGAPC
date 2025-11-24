# pages/20_tipo_usuario_crud.py
import streamlit as st
from db import get_connection

TABLE = "tipodeusuario"
ID_COL = "id_tipo"

st.title("Tipo de usuario — CRUD")

def list_tipos(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_tipo(nombre, apellido, rol):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`nombre`,`apellido`,`rol`) VALUES (%s,%s,%s)",
                        (nombre,apellido,rol))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar tipos de usuario"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar tipos"):
        st.dataframe(list_tipos(limit))

st.markdown("---")
st.subheader("Crear tipo de usuario")
with st.form("create_tipo"):
    nombre = st.text_input("nombre")
    apellido = st.text_input("apellido")
    rol = st.text_input("rol")
    if st.form_submit_button("Crear"):
        ok,msg = create_tipo(nombre,apellido,rol)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_tipo")
buscar = st.text_input("id_tipo")
if st.button("Cargar"):
    if not buscar: st.warning("Ingresa id")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                rec = cur.fetchone()
            if not rec:
                st.info("No encontrado")
            else:
                st.json(rec)
                with st.form("update_tipo"):
                    nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                    apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                    rol = st.text_input("rol", value=str(rec.get("rol") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `nombre`=%s,`apellido`=%s,`rol`=%s WHERE `{ID_COL}`=%s",
                                             (nombre,apellido,rol,buscar))
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
