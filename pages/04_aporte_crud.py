# pages/04_aporte_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "aporte"
ID_COL = "id_aporte"

st.title("Aporte — CRUD")

def list_aportes(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_aporte(id_miembro, id_reunion, monto, fecha, tipo):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_miembro`,`id_reunion`,`monto`,`fecha`,`tipo`) VALUES (%s,%s,%s,%s,%s)",
                        (id_miembro,id_reunion,monto,fecha,tipo))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar aportes"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar aportes"):
        st.dataframe(list_aportes(limit))

st.markdown("---")
st.subheader("Crear aporte")
with st.form("create_aporte"):
    id_miembro = st.text_input("id_miembro")
    id_reunion = st.text_input("id_reunion")
    monto = st.number_input("monto", value=0.0)
    fecha = st.date_input("fecha", value=date.today())
    tipo = st.text_input("tipo")
    if st.form_submit_button("Crear"):
        ok,msg = create_aporte(id_miembro,id_reunion,monto,fecha.isoformat(),tipo)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_aporte")
buscar = st.text_input("id_aporte")
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
                with st.form("update_aporte"):
                    id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                    id_reunion = st.text_input("id_reunion", value=str(rec.get("id_reunion") or ""))
                    monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                    try:
                        fecha_in = date.fromisoformat(str(rec.get("fecha")))
                    except Exception:
                        fecha_in = date.today()
                    fecha_in = st.date_input("fecha", value=fecha_in)
                    tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_miembro`=%s,`id_reunion`=%s,`monto`=%s,`fecha`=%s,`tipo`=%s WHERE `{ID_COL}`=%s",
                                             (id_miembro,id_reunion,monto,fecha_in.isoformat(),tipo,buscar))
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
