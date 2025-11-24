# pages/19_reunion_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "reunion"
ID_COL = "id_reunion"

st.title("Reunión — CRUD")

def list_reuniones(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_reunion(id_grupo, id_asistencia, fecha, dia, lugar, tipo):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_grupo`,`id_asistencia`,`fecha`,`dia`,`lugar`,`extraordinario_ordinario`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (id_grupo,id_asistencia,fecha,dia,lugar,tipo))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar reuniones"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar reuniones"):
        st.dataframe(list_reuniones(limit))

st.markdown("---")
st.subheader("Crear reunión")
with st.form("create_reunion"):
    id_grupo = st.text_input("id_grupo")
    id_asistencia = st.text_input("id_asistencia")
    fecha = st.date_input("fecha", value=date.today())
    dia = st.text_input("dia")
    lugar = st.text_input("lugar")
    tipo = st.selectbox("extraordinario/ordinario", ["extraordinario","ordinario"])
    if st.form_submit_button("Crear"):
        ok,msg = create_reunion(id_grupo,id_asistencia,fecha.isoformat(),dia,lugar,tipo)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_reunion")
buscar = st.text_input("id_reunion")
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
                with st.form("update_reunion"):
                    id_grupo = st.text_input("id_grupo", value=str(rec.get("id_grupo") or ""))
                    id_asistencia = st.text_input("id_asistencia", value=str(rec.get("id_asistencia") or ""))
                    try:
                        fecha_in = date.fromisoformat(str(rec.get("fecha")))
                    except Exception:
                        fecha_in = date.today()
                    fecha_in = st.date_input("fecha", value=fecha_in)
                    dia = st.text_input("dia", value=str(rec.get("dia") or ""))
                    lugar = st.text_input("lugar", value=str(rec.get("lugar") or ""))
                    tipo = st.selectbox("extraordinario/ordinario", ["extraordinario","ordinario"], index=0 if rec.get("extraordinario_ordinario")=="extraordinario" else 1)
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_grupo`=%s,`id_asistencia`=%s,`fecha`=%s,`dia`=%s,`lugar`=%s,`extraordinario_ordinario`=%s WHERE `{ID_COL}`=%s",
                                             (id_grupo,id_asistencia,fecha_in.isoformat(),dia,lugar,tipo,buscar))
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
