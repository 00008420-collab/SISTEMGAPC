# pages/19_reunion_crud.py
import streamlit as st
from db import get_connection

TABLE = "reunion"
ID_COL = "id_reunion"

st.title("Reunion — CRUD")

def list_reuniones(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_reunion(id_grupo,id_asistencia,fecha,dia,lugar,tipo):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_grupo,id_asistencia,fecha,dia,lugar,tipo) VALUES (%s,%s,%s,%s,%s,%s)",
                    (id_grupo,id_asistencia,fecha,dia,lugar,tipo))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def get_by_id(pk):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        r=cur.fetchone(); cur.close(); return r
    finally:
        conn.close()

def update_reunion(pk,id_grupo,id_asistencia,fecha,dia,lugar,tipo):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_grupo=%s,id_asistencia=%s,fecha=%s,dia=%s,lugar=%s,tipo=%s WHERE `{ID_COL}`=%s",
                    (id_grupo,id_asistencia,fecha,dia,lugar,tipo,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_reunion(pk):
    conn=get_connection(); 
    if not conn: return False
    try:
        cur=conn.cursor(); cur.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s",(pk,))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

# UI
with st.expander("Listar reuniones"):
    if st.button("Cargar reuniones"):
        rows=list_reuniones()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear reunion")
with st.form("create_reunion"):
    id_grupo = st.text_input("id_grupo")
    id_asistencia = st.text_input("id_asistencia")
    fecha = st.date_input("fecha")
    dia = st.text_input("dia")
    lugar = st.text_input("lugar")
    tipo = st.selectbox("extraordinario/ordinario", ["extraordinario","ordinario"])
    if st.form_submit_button("Crear"):
        ok=create_reunion(id_grupo,id_asistencia,fecha.isoformat(),dia,lugar,tipo)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar reunion"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_reunion"):
                id_grupo = st.text_input("id_grupo", value=str(rec.get("id_grupo") or ""))
                id_asistencia = st.text_input("id_asistencia", value=str(rec.get("id_asistencia") or ""))
                fecha = st.text_input("fecha", value=str(rec.get("fecha") or ""))
                dia = st.text_input("dia", value=str(rec.get("dia") or ""))
                lugar = st.text_input("lugar", value=str(rec.get("lugar") or ""))
                tipo = st.selectbox("extraordinario/ordinario", ["extraordinario","ordinario"], index=0 if rec.get("tipo")=="extraordinario" else 1)
                if st.form_submit_button("Actualizar"):
                    ok = update_reunion(pk,id_grupo,id_asistencia,fecha,dia,lugar,tipo)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_reunion(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
