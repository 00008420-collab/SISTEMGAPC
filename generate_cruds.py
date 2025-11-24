# generate_cruds.py
import os

PAGES_DIR = "pages"
os.makedirs(PAGES_DIR, exist_ok=True)

# Lista con las 19 tablas exactas (ajusta nombres si tu DB es diferente)
tables = [
 "acta","administrador","ahorro","aporte","asistencia","caja","ciclo","cierre",
 "cuota","directiva","distrito","grupo","miembro","multa","pago","prestamo",
 "promotora","reporte","reunion","tipo_usuario","users"
]

template = """# pages/{file_name}.py
import streamlit as st
from db import run_query
from crud_template_advanced import existing_id_select, money_input, percent_input, estado_select, fk_options, show_table_rows

MODULE_KEY = "page_{file_key}"

def list_rows():
    return run_query("SELECT * FROM {table} ORDER BY 1 DESC LIMIT 500;", fetch=True)

def insert_row_dummy(data_dict):
    # Modifica esta función para insertar segun tus columnas reales
    # Por defecto: intenta insertar keys present in data_dict into table columns
    cols = ", ".join(data_dict.keys())
    placeholders = ", ".join(["%s"]*len(data_dict))
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders});"
    params = tuple(data_dict.values())
    return run_query(q, params, fetch=False)

def render():
    st.title("{pretty}")
    rows = list_rows()
    show_table_rows(rows)
    st.divider()
    st.subheader("Crear / Editar {pretty}")

    with st.form(key=f"form_{MODULE_KEY}"):
        # Ejemplo de campos: ajusta según necesites
        existing = existing_id_select("Seleccionar id existente (opcional)", table="{table}", id_field="id_{table}", key=f"{MODULE_KEY}_existing")
        col1, col2 = st.columns(2)
        with col1:
            campo1 = st.text_input("campo1", key=f"{MODULE_KEY}_campo1")
            monto = money_input("monto (ejemplo)", key=f"{MODULE_KEY}_monto")
        with col2:
            porcentaje = percent_input("interes (%)", key=f"{MODULE_KEY}_interes")
            estado = estado_select("estado", key=f"{MODULE_KEY}_estado")

        submitted = st.form_submit_button("Guardar")
    if submitted:
        # Ajusta data_dict a los campos reales de tu tabla
        data = {"campo1": campo1, "monto": monto, "interes": porcentaje, "estado": estado}
        ok = insert_row_dummy(data)
        if ok:
            st.success("Registro creado/actualizado")
            st.experimental_rerun()
        else:
            st.error("Error al guardar")

if __name__ == "__main__":
    render()
"""

for t in tables:
    file_name = f"{t}_crud"
    file_key = t.replace("_", "")
    pretty = t.replace("_", " ").title()
    content = template.format(file_name=file_name, file_key=file_key, table=t, pretty=pretty)
    path = os.path.join(PAGES_DIR, f"{file_name}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrote", path)

print("Finished generating pages. Revisa y ajusta los campos en cada page según tu esquema de tabla.")
