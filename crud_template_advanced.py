# crud_template_advanced.py
import streamlit as st
from db import run_query

def fk_options(table, id_field="id", label_field=None, where=None, limit=500):
    q = f"SELECT {id_field}"
    if label_field:
        q += f", {label_field}"
    q += f" FROM {table}"
    if where:
        q += f" WHERE {where}"
    q += f" ORDER BY 1 LIMIT {limit};"
    rows = run_query(q, fetch=True)
    if not rows:
        return []
    out = []
    for r in rows:
        if label_field and label_field in r:
            out.append((r[id_field], f"{r[id_field]} — {r[label_field]}"))
        else:
            out.append((r[id_field], str(r[id_field])))
    return out

def existing_id_select(label, table, id_field="id", key=None):
    opts = fk_options(table, id_field=id_field)
    values = [""] + [str(x[0]) for x in opts]
    return st.selectbox(label, options=values, key=key)

def money_input(label, key, value=0.0, step=50.0, min_value=0.0):
    return st.number_input(label, min_value=min_value, value=float(value), step=step, key=key, format="%.2f")

def percent_input(label, key, value=5.0):
    return st.slider(label, min_value=0.0, max_value=100.0, value=float(value), step=0.1, key=key)

def estado_select(label="estado", options=None, key=None):
    if options is None:
        options = ["activo", "inactivo", "pendiente", "pagado", "mora"]
    return st.selectbox(label, options=options, key=key)

def text_input(label, key, placeholder=""):
    return st.text_input(label, key=key, placeholder=placeholder)

def show_table_rows(rows, max_rows=200):
    import pandas as pd
    if not rows:
        st.info("No hay registros.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df.head(max_rows))
