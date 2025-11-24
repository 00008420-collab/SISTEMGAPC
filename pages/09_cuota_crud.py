# pages/09_cuota_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "cuota"
ID_COL = "id_cuota"

st.title("Cuota — CRUD")

def list_cuotas(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_cuota(id_prestamo, fecha_vencimiento, numero, monto_capital, monto_interes, monto_total, estado):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_prestamo`,`fecha_de_vencimiento`,`numero`,`monto_capital`,`monto_interes`,`monto_total`,`estado`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar cuotas"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar cuotas"):
        st.dataframe(list_cuotas(limit))

st.markdown("---")
st.subheader("Crear cuota")
with st.form("create_cuota"):
    id_prestamo = st.text_input("id_prestamo")
    fecha_vencimiento = st.date_input("fecha_de_vencimiento")
    numero = st.number_input("numero", value=1, min_value=1)
    monto_capital = st.number_input("monto_capital", value=0.0)
    monto_interes = st.number_input("monto_interes", value=0.0)
    monto_total = st.number_input("monto_total", value=0.0)
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok,msg = create_cuota(id_prestamo,fecha_vencimiento.isoformat(),numero,monto_capital,monto_interes,monto_total,estado)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_cuota")
buscar = st.text_input("id_cuota")
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
                with st.form("update_cuota"):
                    id_prestamo = st.text_input("id_prestamo", value=str(rec.get("id_prestamo") or ""))
                    try:
                        fv = date.fromisoformat(str(rec.get("fecha_de_vencimiento")))
                    except Exception:
                        fv = date.today()
                    fecha_vencimiento = st.date_input("fecha_de_vencimiento", value=fv)
                    numero = st.number_input("numero", value=int(rec.get("numero") or 1))
                    monto_capital = st.number_input("monto_capital", value=float(rec.get("monto_capital") or 0.0))
                    monto_interes = st.number_input("monto_interes", value=float(rec.get("monto_interes") or 0.0))
                    monto_total = st.number_input("monto_total", value=float(rec.get("monto_total") or 0.0))
                    estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_prestamo`=%s,`fecha_de_vencimiento`=%s,`numero`=%s,`monto_capital`=%s,`monto_interes`=%s,`monto_total`=%s,`estado`=%s WHERE `{ID_COL}`=%s",
                                             (id_prestamo,fecha_vencimiento.isoformat(),numero,monto_capital,monto_interes,monto_total,estado,buscar))
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
