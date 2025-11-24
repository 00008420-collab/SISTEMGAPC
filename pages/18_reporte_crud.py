# pages/18_reporte_crud.py
import streamlit as st
from db import get_connection

TABLE = "reporte"
ID_COL = "id_reporte"

st.title("Reporte — CRUD")

def list_reportes(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_reporte(id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado) VALUES (%s,%s,%s,%s,%s,%s)",
                    (id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado))
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

def update_reporte(pk,id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_ciclo=%s,id_administrador=%s,fecha_generacion=%s,tipo=%s,descripcion=%s,estado=%s WHERE `{ID_COL}`=%s",
                    (id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_reporte(pk):
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
with st.expander("Listar reportes"):
    if st.button("Cargar reportes"):
        rows=list_reportes()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear reporte")
with st.form("create_reporte"):
    id_ciclo = st.text_input("id_ciclo")
    id_administrador = st.text_input("id_administrador")
    fecha_generacion = st.date_input("fecha_generacion")
    tipo = st.text_input("tipo")
    descripcion = st.text_area("descripcion")
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok = create_reporte(id_ciclo,id_administrador,fecha_generacion.isoformat(),tipo,descripcion,estado)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar reporte"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_reporte"):
                id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                id_administrador = st.text_input("id_administrador", value=str(rec.get("id_administrador") or ""))
                fecha_generacion = st.text_input("fecha_generacion", value=str(rec.get("fecha_generacion") or ""))
                tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_reporte(pk,id_ciclo,id_administrador,fecha_generacion,tipo,descripcion,estado)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_reporte(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
