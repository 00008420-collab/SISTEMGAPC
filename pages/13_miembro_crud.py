# pages/13_miembro_crud.py
import streamlit as st
from db import get_connection

TABLE = "miembro"
ID_COL = "id_miembro"

st.title("Miembro — CRUD")

def list_miembros(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_miembro(id_tipousuario, apellido, dui, direccion):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_tipousuario`,`apellido`,`DUI`,`direccion`) VALUES (%s,%s,%s,%s)",
                        (id_tipousuario,apellido,dui,direccion))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar miembros"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar miembros"):
        st.dataframe(list_miembros(limit))

st.markdown("---")
st.subheader("Crear miembro")
with st.form("create_miembro"):
    id_tipousuario = st.text_input("id_tipousuario")
    apellido = st.text_input("apellido")
    dui = st.text_input("DUI")
    direccion = st.text_input("direccion")
    if st.form_submit_button("Crear"):
        ok,msg = create_miembro(id_tipousuario,apellido,dui,direccion)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_miembro")
buscar = st.text_input("id_miembro")
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
                with st.form("update_miembro"):
                    id_tipousuario = st.text_input("id_tipousuario", value=str(rec.get("id_tipousuario") or ""))
                    apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                    dui = st.text_input("DUI", value=str(rec.get("DUI") or ""))
                    direccion = st.text_input("direccion", value=str(rec.get("direccion") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_tipousuario`=%s,`apellido`=%s,`DUI`=%s,`direccion`=%s WHERE `{ID_COL}`=%s",
                                             (id_tipousuario,apellido,dui,direccion,buscar))
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
