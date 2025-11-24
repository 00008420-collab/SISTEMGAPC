# pages/05_asistencia_crud.py
import streamlit as st
from db import get_connection

TABLE = "asistencia"
ID_COL = "id_asistencia"

st.title("Asistencia — CRUD")

def list_asistencias(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_asistencia(id_miembro, id_multa, motivo, presente):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_miembro`,`id_multa`,`motivo`,`presente_ausente`) VALUES (%s,%s,%s,%s)",
                        (id_miembro,id_multa,motivo,presente))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar asistencias"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar asistencias"):
        st.dataframe(list_asistencias(limit))

st.markdown("---")
st.subheader("Crear asistencia")
with st.form("create_asistencia"):
    id_miembro = st.text_input("id_miembro")
    id_multa = st.text_input("id_multa")
    motivo = st.text_input("motivo")
    presente = st.selectbox("presente/ausente", ["presente","ausente"])
    if st.form_submit_button("Crear"):
        ok,msg = create_asistencia(id_miembro,id_multa,motivo,presente)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_asistencia")
buscar = st.text_input("id_asistencia")
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
                with st.form("update_asistencia"):
                    id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                    id_multa = st.text_input("id_multa", value=str(rec.get("id_multa") or ""))
                    motivo = st.text_input("motivo", value=str(rec.get("motivo") or ""))
                    presente = st.selectbox("presente/ausente", ["presente","ausente"], index=0 if rec.get("presente_ausente")=="presente" else 1)
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_miembro`=%s,`id_multa`=%s,`motivo`=%s,`presente_ausente`=%s WHERE `{ID_COL}`=%s",
                                             (id_miembro,id_multa,motivo,presente,buscar))
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
