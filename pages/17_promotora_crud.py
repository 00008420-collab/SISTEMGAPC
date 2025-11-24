# pages/17_promotora_crud.py
import streamlit as st
from db import get_connection

TABLE = "promotora"
ID_COL = "id_promotora"

st.title("Promotora — CRUD")

def list_promotoras(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_promotora(id_administrador, nombre, apellido, telefono, correo, distrito):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_administrador`,`nombre`,`apellido`,`telefono`,`correo`,`distrito`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (id_administrador,nombre,apellido,telefono,correo,distrito))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar promotoras"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar promotoras"):
        st.dataframe(list_promotoras(limit))

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
        ok,msg = create_promotora(id_administrador,nombre,apellido,telefono,correo,distrito)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_promotora")
buscar = st.text_input("id_promotora")
if st.button("Cargar"):
    if not buscar: st.warning("Ingresa id")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                rec = cur.fetchone()
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
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_administrador`=%s,`nombre`=%s,`apellido`=%s,`telefono`=%s,`correo`=%s,`distrito`=%s WHERE `{ID_COL}`=%s",
                                             (id_administrador,nombre,apellido,telefono,correo,distrito,buscar))
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
