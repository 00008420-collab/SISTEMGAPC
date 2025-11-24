# pages/07_ciclo_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "ciclo"
ID_COL = "id_ciclo"

st.title("Ciclo — CRUD")

def list_ciclos(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_ciclo(fecha_inicio, fecha_fin, estado, total_utilidad):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`fecha_inicio`,`fecha_fin`,`estado`,`total_utilidad`) VALUES (%s,%s,%s,%s)",
                        (fecha_inicio,fecha_fin,estado,total_utilidad))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar ciclos"):
    limit = st.number_input("Límite", value=200, min_value=10)
    if st.button("Cargar ciclos"):
        st.dataframe(list_ciclos(limit))

st.markdown("---")
st.subheader("Crear ciclo")
with st.form("create_ciclo"):
    fecha_inicio = st.date_input("fecha_inicio", value=date.today())
    fecha_fin = st.date_input("fecha_fin", value=date.today())
    estado = st.text_input("estado")
    total_utilidad = st.number_input("total_utilidad", value=0.0)
    if st.form_submit_button("Crear"):
        ok,msg = create_ciclo(fecha_inicio.isoformat(),fecha_fin.isoformat(),estado,total_utilidad)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_ciclo")
buscar = st.text_input("id_ciclo")
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
                with st.form("update_ciclo"):
                    try:
                        fi = date.fromisoformat(str(rec.get("fecha_inicio")))
                        ff = date.fromisoformat(str(rec.get("fecha_fin")))
                    except Exception:
                        fi = date.today(); ff = date.today()
                    fecha_inicio = st.date_input("fecha_inicio", value=fi)
                    fecha_fin = st.date_input("fecha_fin", value=ff)
                    estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                    total_utilidad = st.number_input("total_utilidad", value=float(rec.get("total_utilidad") or 0.0))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `fecha_inicio`=%s,`fecha_fin`=%s,`estado`=%s,`total_utilidad`=%s WHERE `{ID_COL}`=%s",
                                             (fecha_inicio.isoformat(),fecha_fin.isoformat(),estado,total_utilidad,buscar))
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
