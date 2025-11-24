# pages/03_ahorro_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "ahorro"
ID_COL = "id_ahorro"

st.title("Ahorro — CRUD")

def list_ahorros(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_ahorro(id_miembro, monto_actual, saldo_actual, fecha_actualizacion):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_miembro`,`monto_actual`,`saldo_actual`,`fecha_de_actualizacion`) VALUES (%s,%s,%s,%s)",
                        (id_miembro,monto_actual,saldo_actual,fecha_actualizacion))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar ahorros"):
    limit = st.number_input("Límite", value=200, min_value=10)
    if st.button("Cargar ahorros"):
        st.dataframe(list_ahorros(limit))

st.markdown("---")
st.subheader("Crear ahorro")
with st.form("create_ahorro"):
    id_miembro = st.text_input("id_miembro")
    monto_actual = st.number_input("monto_actual", value=0.0, format="%f")
    saldo_actual = st.number_input("saldo_actual", value=0.0, format="%f")
    fecha = st.date_input("fecha_de_actualizacion", value=date.today())
    if st.form_submit_button("Crear"):
        ok,msg = create_ahorro(id_miembro,monto_actual,saldo_actual,fecha.isoformat())
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_ahorro")
buscar = st.text_input("id_ahorro")
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
                with st.form("update_ahorro"):
                    id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                    monto_actual = st.number_input("monto_actual", value=float(rec.get("monto_actual") or 0.0))
                    saldo_actual = st.number_input("saldo_actual", value=float(rec.get("saldo_actual") or 0.0))
                    try:
                        fecha_in = st.date_input("fecha_de_actualizacion", value=date.fromisoformat(str(rec.get("fecha_de_actualizacion"))))
                    except Exception:
                        fecha_in = st.date_input("fecha_de_actualizacion")
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_miembro`=%s,`monto_actual`=%s,`saldo_actual`=%s,`fecha_de_actualizacion`=%s WHERE `{ID_COL}`=%s",
                                             (id_miembro,monto_actual,saldo_actual,fecha_in.isoformat(),buscar))
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
