# pages/14_multa_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "multa"
ID_COL = "id_multa"

st.title("Multa — CRUD")

def list_multas(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_multa(id_miembro, tipo, monto, descripcion, fecha, estado):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_miembro`,`tipo`,`monto`,`descripcion`,`fecha`,`estado`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (id_miembro,tipo,monto,descripcion,fecha,estado))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar multas"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar multas"):
        st.dataframe(list_multas(limit))

st.markdown("---")
st.subheader("Crear multa")
with st.form("create_multa"):
    id_miembro = st.text_input("id_miembro")
    tipo = st.text_input("tipo")
    monto = st.number_input("monto", value=0.0)
    descripcion = st.text_area("descripcion")
    fecha = st.date_input("fecha", value=date.today())
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok,msg = create_multa(id_miembro,tipo,monto,descripcion,fecha.isoformat(),estado)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_multa")
buscar = st.text_input("id_multa")
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
                with st.form("update_multa"):
                    id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                    tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                    monto = st.number_input("monto", value=float(rec.get("monto") or 0.0))
                    descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                    try:
                        fecha_in = date.fromisoformat(str(rec.get("fecha")))
                    except Exception:
                        fecha_in = date.today()
                    fecha_in = st.date_input("fecha", value=fecha_in)
                    estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_miembro`=%s,`tipo`=%s,`monto`=%s,`descripcion`=%s,`fecha`=%s,`estado`=%s WHERE `{ID_COL}`=%s",
                                             (id_miembro,tipo,monto,descripcion,fecha_in.isoformat(),estado,buscar))
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
