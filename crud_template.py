# crud_template.py
import streamlit as st
from db import run_query

def render_crud(table_name: str, pk: str, columns: list):
    """
    table_name: nombre de la tabla en la BD
    pk: nombre de la columna PK (ej: id_acta)
    columns: lista de columnas (incluyendo pk)
    """
    st.header(f"{table_name} - CRUD")
    # listar
    rows = run_query(f"SELECT * FROM `{table_name}`", fetch=True)
    if rows is None:
        st.warning("No se pudieron obtener registros (revisa logs).")
        return

    st.subheader("Registros")
    if len(rows) == 0:
        st.info("No hay registros.")
    else:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df)

    st.subheader("Crear nuevo")
    with st.form(f"form_create_{table_name}"):
        data = {}
        for col in columns:
            if col == pk:
                continue  # omitimos pk (auto)
            # campos simples: texto; el usuario puede adaptar
            data[col] = st.text_input(f"{col}", key=f"create_{table_name}_{col}")
        submitted = st.form_submit_button("Crear")
        if submitted:
            cols = [c for c in columns if c != pk]
            vals = [data[c] for c in cols]
            placeholders = ", ".join(["%s"] * len(vals))
            cols_sql = ", ".join([f"`{c}`" for c in cols])
            sql = f"INSERT INTO `{table_name}` ({cols_sql}) VALUES ({placeholders})"
            ok = run_query(sql, tuple(vals), fetch=False)
            if ok:
                st.success("Registro creado.")
                st.experimental_rerun()
            else:
                st.error("No se pudo crear el registro.")

    st.subheader("Eliminar (por id)")
    with st.form(f"form_delete_{table_name}"):
        id_to_delete = st.text_input("ID a eliminar", key=f"del_{table_name}")
        if st.form_submit_button("Eliminar"):
            sql = f"DELETE FROM `{table_name}` WHERE `{pk}`=%s"
            ok = run_query(sql, (id_to_delete,), fetch=False)
            if ok:
                st.success("Eliminado.")
                st.experimental_rerun()
            else:
                st.error("Fallo al eliminar.")
