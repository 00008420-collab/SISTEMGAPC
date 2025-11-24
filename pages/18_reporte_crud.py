# pages/18_reporte_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "reporte"
ID_COL = "id_reporte"

st.title("Reporte — CRUD")

def list_reportes(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_reporte(id_ciclo, id_administrador, fecha_generacion, tipo, descripcion, estado):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_ciclo`,`id_administrador`,`fecha_de_generacion`,`tipo`,`descripcion`,`estado`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar reportes"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar reportes"):
        st.dataframe(list_reportes(limit))

st.markdown("---")
st.subheader("Crear reporte")
with st.form("create_reporte"):
    id_ciclo = st.text_input("id_ciclo")
    id_administrador = st.text_input("id_administrador")
    fecha_generacion = st.date_input("fecha_de_generacion", value=date.today())
    tipo = st.text_input("tipo")
    descripcion = st.text_area("descripcion")
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok,msg = create_reporte(id_ciclo,id_administrador,fecha_generacion.isoformat(),tipo,descripcion,estado)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_reporte")
buscar = st.text_input("id_reporte")
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
                with st.form("update_reporte"):
                    id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                    id_administrador = st.text_input("id_administrador", value=str(rec.get("id_administrador") or ""))
                    try:
                        fg = date.fromisoformat(str(rec.get("fecha_de_generacion")))
                    except Exception:
                        fg = date.today()
                    fecha_generacion = st.date_input("fecha_de_generacion", value=fg)
                    tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                    descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                    estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_ciclo`=%s,`id_administrador`=%s,`fecha_de_generacion`=%s,`tipo`=%s,`descripcion`=%s,`estado`=%s WHERE `{ID_COL}`=%s",
                                             (id_ciclo,id_administrador,fecha_generacion.isoformat(),tipo,descripcion,estado,buscar))
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
