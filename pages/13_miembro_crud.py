# pages/13_miembro_crud.py
import streamlit as st
from db import get_connection

TABLE = "miembro"
ID_COL = "id_miembro"

st.title("Miembro — CRUD")

def list_miembros(limit=200):
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

def create_miembro(id_tipo_usuario, apellido, dui, direccion):
    conn = get_connection()
    if not conn:
        return False, "no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO `{TABLE}` (`id_tipo_usuario`,`apellido`,`dui`,`direccion`) VALUES (%s,%s,%s,%s)",
                (id_tipo_usuario, apellido, dui, direccion),
            )
            conn.commit()
            return True, "Creado"
    except Exception as e:
        return False, str(e)
    finally:
        try:
            conn.close()
        except Exception:
            pass

with st.expander("Listar miembros"):
    limit = st.number_input("Límite", value=200, min_value=10)
    if st.button("Cargar miembros"):
        st.dataframe(list_miembros(limit))

st.markdown("---")
st.subheader("Crear miembro")
with st.form("create_miembro"):
    id_tipo_usuario = st.text_input("id_tipo_usuario")
    apellido = st.text_input("apellido")
    dui = st.text_input("dui")
    direccion = st.text_input("direccion")
    if st.form_submit_button("Crear"):
        ok, msg = create_miembro(id_tipo_usuario, apellido, dui, direccion)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_miembro")
buscar = st.text_input("id_miembro")
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
            with st.form("update_miembro"):
                id_tipo_usuario = st.text_input("id_tipo_usuario", value=str(rec.get("id_tipo_usuario") or ""))
                apellido = st.text_input("apellido", value=str(rec.get("apellido") or ""))
                dui = st.text_input("dui", value=str(rec.get("dui") or ""))
                direccion = st.text_input("direccion", value=str(rec.get("direccion") or ""))
                if st.form_submit_button("Actualizar"):
                    try:
                        conn2 = get_connection()
                        with conn2.cursor() as cur2:
                            cur2.execute(
                                f"UPDATE `{TABLE}` SET `id_tipo_usuario`=%s,`apellido`=%s,`dui`=%s,`direccion`=%s WHERE `{ID_COL}`=%s",
                                (id_tipo_usuario, apellido, dui, direccion, buscar),
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
