# pages/XX_table_crud.py  -> copia este template y cambia TABLE e ID_COL
import streamlit as st
from db import get_connection
from crud_utils import get_columns_from_db

# EDITA ESTAS DOS CONSTANTES al crear el archivo concreto
TABLE = "REPLACE_TABLE"
ID_COL = "REPLACE_IDCOL"

st.title(f"{TABLE.capitalize()} — CRUD")

cols = get_columns_from_db(TABLE)
if not cols:
    st.warning(f"No se detectan columnas para la tabla '{TABLE}'. Comprueba el nombre.")
else:
    st.write("Columnas detectadas:", cols)

with st.expander("Listar registros"):
    limit = st.number_input("Límite de filas", min_value=10, max_value=2000, value=200, step=10)
    if st.button(f"Cargar {TABLE}"):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s", (int(limit),))
                rows = cur.fetchall()
            st.dataframe(rows)
            st.success(f"{len(rows)} filas cargadas")
        except Exception as e:
            st.error(f"Error cargando registros: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

st.markdown("---")
st.subheader("Crear nuevo registro")
if cols:
    with st.form(f"create_{TABLE}"):
        inputs = {}
        for c in cols:
            if c == ID_COL:
                continue
            if "fecha" in c.lower():
                inputs[c] = st.date_input(c)
            else:
                inputs[c] = st.text_input(c)
        if st.form_submit_button("Crear"):
            payload_cols = []
            payload_vals = []
            for k,v in inputs.items():
                payload_cols.append(f"`{k}`")
                # conversión simple
                if hasattr(v, "isoformat"):
                    payload_vals.append(v.isoformat())
                else:
                    payload_vals.append(v)
            placeholders = ", ".join(["%s"] * len(payload_vals))
            sql = f"INSERT INTO `{TABLE}` ({', '.join(payload_cols)}) VALUES ({placeholders})"
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(payload_vals))
                    conn.commit()
                    st.success("Registro creado.")
            except Exception as e:
                st.error(f"Error creando registro: {e}")
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por ID")
buscar_id = st.text_input(f"Introduce {ID_COL} a buscar", "")
if st.button("Cargar registro"):
    if not buscar_id:
        st.warning("Ingresa un id válido.")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}` = %s LIMIT 1", (buscar_id,))
                rec = cur.fetchone()
            if not rec:
                st.info("No se encontró ese registro.")
            else:
                st.json(rec)
                with st.form(f"update_{TABLE}"):
                    updated = {}
                    for c in cols:
                        if c == ID_COL:
                            st.text_input(c, value=str(rec.get(c)), disabled=True)
                        else:
                            updated[c] = st.text_input(c, value=str(rec.get(c) or ""))
                    if st.form_submit_button("Actualizar"):
                        set_clause = ", ".join([f"`{k}` = %s" for k in updated.keys()])
                        params = list(updated.values()) + [buscar_id]
                        update_sql = f"UPDATE `{TABLE}` SET {set_clause} WHERE `{ID_COL}` = %s"
                        conn2 = get_connection()
                        try:
                            with conn2.cursor() as cur2:
                                cur2.execute(update_sql, tuple(params))
                                conn2.commit()
                                st.success("Registro actualizado.")
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")
                        finally:
                            try:
                                conn2.close()
                            except Exception:
                                pass

                if st.button("Eliminar registro"):
                    conn3 = get_connection()
                    try:
                        with conn3.cursor() as cur3:
                            cur3.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}` = %s", (buscar_id,))
                            conn3.commit()
                            st.success("Registro eliminado (si existía).")
                    except Exception as e:
                        st.error(f"Error al eliminar: {e}")
                    finally:
                        try:
                            conn3.close()
                        except Exception:
                            pass
