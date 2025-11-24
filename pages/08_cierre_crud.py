# pages/08_cierre_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "cierre"
ID_COL = "id_cierre"

st.title("Cierre — CRUD")

def list_cierres(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_cierre(id_ciclo, fecha, descripcion):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_ciclo`,`fecha`,`descripcion`) VALUES (%s,%s,%s)",
                        (id_ciclo,fecha,descripcion))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar cierres"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar cierres"):
        st.dataframe(list_cierres(limit))

st.markdown("---")
st.subheader("Crear cierre")
with st.form("create_cierre"):
    id_ciclo = st.text_input("id_ciclo")
    fecha = st.date_input("fecha")
    descripcion = st.text_area("descripcion")
    if st.form_submit_button("Crear"):
        ok,msg = create_cierre(id_ciclo,fecha.isoformat(),descripcion)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_cierre")
buscar = st.text_input("id_cierre")
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
                with st.form("update_cierre"):
                    id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                    try:
                        fecha_in = date.fromisoformat(str(rec.get("fecha")))
                    except Exception:
                        fecha_in = date.today()
                    fecha_in = st.date_input("fecha", value=fecha_in)
                    descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_ciclo`=%s,`fecha`=%s,`descripcion`=%s WHERE `{ID_COL}`=%s",
                                             (id_ciclo,fecha_in.isoformat(),descripcion,buscar))
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
