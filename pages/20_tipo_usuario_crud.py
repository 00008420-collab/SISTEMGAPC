# pages/20_tipo_usuario_crud.py
import streamlit as st
from db import get_connection

TABLE = "tipo_usuario"
ID_COL = "id_tipo_usuario"

st.title("Tipo de usuario — CRUD")

def list_tipos(limit=200):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s", (limit,))
            return cur.fetchall()
    finally:
        try:
            conn.close()
        except Exception:
            pass

def create_tipo(nombre, apellido, rol):
    conn = get_connection()
    if not conn:
        return False, "no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`nombre`,`apellido`,`rol`) VALUES (%s,%s,%s)", (nombre, apellido, rol))
            conn.commit()
            return True, "Creado"
    except Exception as e:
        return False, str(e)
    finally:
        try:
            conn.close()
        except Exception:
            pass

with st.expander("Listar tipos de usuario"):
    limit = st.number_input("Límite", value=200, min_value=10)
    if st.button("Cargar tipos"):
        st.dataframe(list_tipos(limit))

st.markdown("---")
st.subheader("Crear tipo de usuario")
with st.form("create_tipo"):
    nombre = st.text_input("nombre")
    apellido = st.text_input("apellido")
    rol = st.text_input("rol")
    if st.form_submit_button("Crear"):
        ok, msg = create_tipo(nombre, apellido, rol)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_tipo_usuario")
buscar = st.text_input("id_tipo_usuario")
if st.button("Cargar"):
    if not buscar:
        st.warning("Ingresa id")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s", (buscar,))
                rec = cur.fetchone()
        except Exception as e:
            st.error(f"Error al consultar: {e}")
            rec = None
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not rec:
            st.info("No encontrado")
        else:
            st.json(rec)
            with st.form("update_tipo"):
                nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                rol = st.text_input("rol", value=str(rec.get("rol") or ""))
                if st.form_submit_button("Actualizar"):
                    try:
                        conn2 = get_connection()
                        with conn2.cursor() as cur2:
                            cur2.execute(
                                f"UPDATE `{TABLE}` SET `nombre`=%s,`apellido`=%s,`rol`=%s WHERE `{ID_COL}`=%s",
                                (nombre, apellido, rol, buscar),
                            )
                            conn2.commit()
                        st.success("Actualizado")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        try:
                            conn2.close()
                        except Exception:
                            pass

            if st.button("Eliminar"):
                try:
                    conn3 = get_connection()
                    with conn3.cursor() as cur3:
                        cur3.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s", (buscar,))
                        conn3.commit()
                    st.success("Eliminado")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    try:
                        conn3.close()
                    except Exception:
                        pass
