# pages/01_acta_crud.py
import streamlit as st
from db import get_connection

TABLE = "acta"
ID_COL = "id_acta"

st.title("Acta — CRUD")

def list_actas(limit=200):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def create_acta(id_ciclo, tipo, fecha, descripcion):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO `{TABLE}` (id_ciclo,tipo,fecha,descripcion) VALUES (%s,%s,%s,%s)",
            (id_ciclo, tipo, fecha, descripcion),
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        st.error(e)
        return False
    finally:
        conn.close()

def get_by_id(pk):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s", (pk,))
        r = cur.fetchone()
        cur.close()
        return r
    finally:
        conn.close()

def update_acta(pk, id_ciclo, tipo, fecha, descripcion):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE `{TABLE}` SET id_ciclo=%s,tipo=%s,fecha=%s,descripcion=%s WHERE `{ID_COL}`=%s",
            (id_ciclo, tipo, fecha, descripcion, pk),
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        st.error(e)
        return False
    finally:
        conn.close()

def delete_acta(pk):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s", (pk,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        st.error(e)
        return False
    finally:
        conn.close()

# UI
with st.expander("Listar actas"):
    limit = st.number_input("Límite", value=200, min_value=1)
    if st.button("Cargar actas"):
        rows = list_actas(limit)
        if rows is None:
            st.error("No hay conexión")
        else:
            st.dataframe(rows)

st.markdown("---")
st.subheader("Crear acta")
with st.form("create"):
    id_ciclo = st.text_input("id_ciclo")
    tipo = st.text_input("tipo")
    fecha = st.date_input("fecha")
    descripcion = st.text_area("descripcion")
    if st.form_submit_button("Crear"):
        ok = create_acta(id_ciclo, tipo, fecha.isoformat(), descripcion)
        if ok:
            st.success("Creado")
        else:
            st.error("Error al crear")

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar")
pk = st.text_input(ID_COL)
if st.button("Cargar"):
    if not pk:
        st.warning("Ingresa id")
    else:
        rec = get_by_id(pk)
        if not rec:
            st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update"):
                id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                tipo = st.text_input("tipo", value=str(rec.get("tipo") or ""))
                fecha_val = str(rec.get("fecha") or "")
                descripcion = st.text_area("descripcion", value=str(rec.get("descripcion") or ""))
                if st.form_submit_button("Actualizar"):
                    ok = update_acta(pk, id_ciclo, tipo, fecha_val, descripcion)
                    if ok:
                        st.success("Actualizado")
                    else:
                        st.error("Error al actualizar")
            if st.button("Eliminar"):
                if delete_acta(pk):
                    st.success("Eliminado")
                else:
                    st.error("Error al eliminar")
