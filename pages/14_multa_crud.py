# pages/14_multa_crud.py
import streamlit as st
from db import get_connection

TABLE = "multa"
ID_COL = "id_multa"

st.title("Multa — CRUD")

def list_multas(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_multa(id_miembro,tipo,monto,descripcion,fecha,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_miembro,tipo,monto,descripcion,fecha,estado) VALUES (%s,%s,%s,%s,%s,%s)",
                    (id_miembro,tipo,monto,descripcion,fecha,estado))
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

def update_multa(pk,id_miembro,tipo,monto,descripcion,fecha,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_miembro=%s,tipo=%s,monto=%s,descripcion=%s,fecha=%s,estado=%s WHERE `{ID_COL}`=%s",
                    (id_miembro,tipo,monto,descripcion,fecha,estado,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_multa(pk):
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
with st.expander("Listar multas"):
    if st.button("Cargar multas"):
        rows=list_multas()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear multa")
with st.form("create_multa"):
    id_miembro = st.text_input("id_miembro")
    tipo = st.text_input("tipo")
    monto = st.number_input("monto", value=0.0)
    descripcion = st.text_area("descripcion")
    fecha = st.date_input("fecha")
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok=create_multa(id_miembro,tipo,monto,descripcion,fecha.isoformat(),estado)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar multa"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_multa"):
                id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                fecha = st.text_input("fecha", value=str(rec.get("fecha") or ""))
                estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_multa(pk,id_miembro,tipo,monto,descripcion,fecha,estado)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_multa(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
