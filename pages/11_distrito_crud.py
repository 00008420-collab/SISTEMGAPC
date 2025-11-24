# pages/11_distrito_crud.py
import streamlit as st
from db import get_connection

TABLE = "distrito"
ID_COL = "id_distrito"

st.title("Distrito — CRUD")

def list_distritos(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_distrito(id_grupo, nombre, lugar):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_grupo`,`nombre`,`lugar`) VALUES (%s,%s,%s)",
                        (id_grupo,nombre,lugar))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar distritos"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar distritos"):
        st.dataframe(list_distritos(limit))

st.markdown("---")
st.subheader("Crear distrito")
with st.form("create_distrito"):
    id_grupo = st.text_input("id_grupo")
    nombre = st.text_input("nombre")
    lugar = st.text_input("lugar")
    if st.form_submit_button("Crear"):
        ok,msg = create_distrito(id_grupo,nombre,lugar)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_distrito")
buscar = st.text_input("id_distrito")
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
                with st.form("update_distrito"):
                    id_grupo = st.text_input("id_grupo", value=str(rec.get("id_grupo") or ""))
                    nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                    lugar = st.text_input("lugar", value=str(rec.get("lugar") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_grupo`=%s,`nombre`=%s,`lugar`=%s WHERE `{ID_COL}`=%s",
                                             (id_grupo,nombre,lugar,buscar))
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
