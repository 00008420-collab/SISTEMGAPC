# pages/12_grupo_crud.py
import streamlit as st
from db import get_connection

TABLE = "grupo"
ID_COL = "id_grupo"

st.title("Grupo — CRUD")

def list_grupos(limit=200):
    conn=get_connection(); 
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_grupo(id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado))
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

def update_grupo(pk,id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_ciclo=%s,id_miembro=%s,id_administrador=%s,id_promotora=%s,nombre=%s,fecha_inicio=%s,fecha_interes=%s,tipo_multa=%s,frecuencia_reuniones=%s,politicas_prestamo=%s,estado=%s WHERE `{ID_COL}`=%s",
                    (id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_grupo(pk):
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
with st.expander("Listar grupos"):
    if st.button("Cargar grupos"):
        rows=list_grupos()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear grupo")
with st.form("create_grupo"):
    id_ciclo = st.text_input("id_ciclo")
    id_miembro = st.text_input("id_miembro")
    id_administrador = st.text_input("id_administrador")
    id_promotora = st.text_input("id_promotora")
    nombre = st.text_input("nombre")
    fecha_inicio = st.date_input("fecha_inicio")
    fecha_interes = st.text_input("fecha_interes")
    tipo_multa = st.text_input("tipo_multa")
    frecuencia_reuniones = st.text_input("frecuencia_reuniones")
    politicas_prestamo = st.text_area("politicas_prestamo")
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok=create_grupo(id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio.isoformat(),fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk=st.text_input(ID_COL)
if st.button("Cargar grupo"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_grupo"):
                id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                id_administrador = st.text_input("id_administrador", value=str(rec.get("id_administrador") or ""))
                id_promotora = st.text_input("id_promotora", value=str(rec.get("id_promotora") or ""))
                nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                fecha_inicio = st.text_input("fecha_inicio", value=str(rec.get("fecha_inicio") or ""))
                fecha_interes = st.text_input("fecha_interes", value=str(rec.get("fecha_interes") or ""))
                tipo_multa = st.text_input("tipo_multa", value=str(rec.get("tipo_multa") or ""))
                frecuencia_reuniones = st.text_input("frecuencia_reuniones", value=str(rec.get("frecuencia_reuniones") or ""))
                politicas_prestamo = st.text_area("politicas_prestamo", value=str(rec.get("politicas_prestamo") or ""))
                estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_grupo(pk,id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_grupo(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
