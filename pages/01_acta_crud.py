# pages/01_acta_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "acta"
ID_COL = "id_acta"

st.title("Acta — CRUD")

def list_records(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s", (limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_record(id_ciclo, tipo, fecha, descripcion):
    conn = get_connection()
    if not conn: return False, "No connection"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_ciclo`,`tipo`,`fecha`,`descripcion`) VALUES (%s,%s,%s,%s)",
                        (id_ciclo, tipo, fecha, descripcion))
            conn.commit()
            return True, "Creado"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Listado
with st.expander("Listar actas"):
    limit = st.number_input("Límite", min_value=10, max_value=2000, value=200)
    if st.button("Cargar actas"):
        rows = list_records(limit)
        st.dataframe(rows)

st.markdown("---")
st.subheader("Crear acta")
with st.form("create_acta"):
    id_ciclo = st.text_input("id_ciclo")
    tipo = st.text_input("tipo")
    fecha = st.date_input("fecha", value=date.today())
    descripcion = st.text_area("descripcion")
    if st.form_submit_button("Crear"):
        ok,msg = create_record(id_ciclo,tipo,fecha.isoformat(),descripcion)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_acta")
buscar = st.text_input("id_acta")
if st.button("Cargar"):
    if not buscar: st.warning("Ingresa id_acta")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s LIMIT 1",(buscar,))
                rec = cur.fetchone()
            if not rec:
                st.info("No encontrado")
            else:
                st.json(rec)
                with st.form("update_acta"):
                    id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                    tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                    fecha_val = rec.get("fecha")
                    try:
                        from datetime import date
                        fecha_in = st.date_input("fecha", value=date.fromisoformat(str(fecha_val)))
                    except Exception:
                        fecha_in = st.date_input("fecha")
                    descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_ciclo`=%s,`tipo`=%s,`fecha`=%s,`descripcion`=%s WHERE `{ID_COL}`=%s",
                                             (id_ciclo,tipo,fecha_in.isoformat(),descripcion,buscar))
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
