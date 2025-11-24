# pages/09_cuota_crud.py
import streamlit as st
from db import get_connection

TABLE = "cuota"
ID_COL = "id_cuota"

st.title("Cuota — CRUD")

def list_cuotas(limit=200):
    conn=get_connection()
    if not conn: return None
    try:
        cur=conn.cursor(dictionary=True); cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
        rows=cur.fetchall(); cur.close(); return rows
    finally:
        conn.close()

def create_cuota(id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"INSERT INTO `{TABLE}` (id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado))
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

def update_cuota(pk,id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado):
    conn=get_connection()
    if not conn: return False
    try:
        cur=conn.cursor()
        cur.execute(f"UPDATE `{TABLE}` SET id_prestamo=%s,fecha_vencimiento=%s,numero=%s,monto_capital=%s,monto_interes=%s,monto_total=%s,estado=%s WHERE `{ID_COL}`=%s",
                    (id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado,pk))
        conn.commit(); cur.close(); return True
    except Exception as e:
        st.error(e); return False
    finally:
        conn.close()

def delete_cuota(pk):
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
with st.expander("Listar cuotas"):
    if st.button("Cargar cuotas"):
        rows=list_cuotas()
        if rows is None: st.error("No conexión")
        else: st.dataframe(rows)

st.markdown("---")
st.subheader("Crear cuota")
with st.form("create_cuota"):
    id_prestamo = st.text_input("id_prestamo")
    fecha_vencimiento = st.date_input("fecha_vencimiento")
    numero = st.number_input("numero", value=1, min_value=1)
    monto_capital = st.number_input("monto_capital", value=0.0)
    monto_interes = st.number_input("monto_interes", value=0.0)
    monto_total = st.number_input("monto_total", value=0.0)
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok=create_cuota(id_prestamo,fecha_vencimiento.isoformat(),numero,monto_capital,monto_interes,monto_total,estado)
        st.success("Creado" if ok else "Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar cuota"):
    if not pk: st.warning("Ingresa id")
    else:
        rec=get_by_id(pk)
        if not rec: st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_cuota"):
                id_prestamo = st.text_input("id_prestamo", value=str(rec.get("id_prestamo") or ""))
                fecha_vencimiento = st.text_input("fecha_vencimiento", value=str(rec.get("fecha_vencimiento") or ""))
                numero = st.number_input("numero", value=int(rec.get("numero") or 1))
                monto_capital = st.number_input("monto_capital", value=float(rec.get("monto_capital") or 0.0))
                monto_interes = st.number_input("monto_interes", value=float(rec.get("monto_interes") or 0.0))
                monto_total = st.number_input("monto_total", value=float(rec.get("monto_total") or 0.0))
                estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_cuota(pk,id_prestamo,fecha_vencimiento,numero,monto_capital,monto_interes,monto_total,estado)
                    st.success("Actualizado" if ok else "Error al actualizar")
            if st.button("Eliminar"):
                ok = delete_cuota(pk)
                st.success("Eliminado" if ok else "Error al eliminar")
