# generate_cruds.py
"""
Generador automático de archivos CRUD para 19 tablas.
Requisitos: tener db.py con run_query() y get_table_names() accesibles desde el repo.
Ejecutar en la raíz del repo: python generate_cruds.py
"""

import os
from textwrap import dedent

PAGES_DIR = "pages"
os.makedirs(PAGES_DIR, exist_ok=True)

# lista ordenada de tablas y nombres legibles (19)
tables = [
    ("acta", "Acta"),
    ("administrador", "Administrador"),
    ("ahorro", "Ahorro"),
    ("aporte", "Aporte"),
    ("asistencia", "Asistencia"),
    ("cuota", "Cuota"),
    ("prestamo", "Prestamo"),
    ("grupo", "Grupo"),
    ("miembro", "Miembro"),
    ("multa", "Multa"),
    ("tipo_usuario", "Tipo_usuario"),
    ("reunion", "Reunion"),
    ("pago", "Pago"),
    ("promotora", "Promotora"),
    ("directiva", "Directiva"),
    ("ciclo", "Ciclo"),
    ("reporte", "Reporte"),
    ("caja", "Caja"),
    ("distrito", "Distrito"),
]

# plantilla general para la mayoría de tablas
crud_template = dedent("""
    # {filename}
    import streamlit as st
    from db import run_query

    st.set_page_config(layout="wide")
    PREFIX = "{table}_"

    st.title("{readable} — CRUD")
    st.write("CRUD dinámico para la tabla `{table}`. Los campos se obtienen con SHOW COLUMNS.")

    def get_columns():
        q = "SHOW COLUMNS FROM `{table}`;"
        rows = run_query(q, fetch=True)
        if rows is None:
            st.error("Error al obtener columnas (revisa logs)")
            return []
        # rows: [{'Field': 'id', 'Type': 'int(11)', ...}, ...]
        cols = [r['Field'] for r in rows]
        return cols

    cols = get_columns()
    if not cols:
        st.info("No se detectaron columnas para la tabla.")
        st.stop()

    # PANEL de búsqueda / lista
    with st.expander("Buscar / Listar registros", expanded=True):
        q_all = "SELECT * FROM `{table}` LIMIT 200;"
        data = run_query(q_all, fetch=True)
        if data is None:
            st.error("Error al listar registros. Revisa la conexión.")
        else:
            st.write(f"Mostrando hasta 200 registros (total: {len(data)})")
            st.dataframe(data)

    # FORM crear
    with st.form(key=PREFIX + "create_form"):
        st.subheader("Crear nuevo registro")
        values = {{}}
        # generamos inputs básicos: si el nombre de campo incluye 'fecha' -> date_input, 'id' se omite en creación si es auto-increment
        for c in cols:
            if c.lower().startswith("id_") or c.lower()=="id":
                # si el campo es llave primaria, ofrezco input opcional pero por defecto vacío (para dejar que BD auto-asigne)
                values[c] = st.text_input(f"{c} (dejar vacío para auto)", key=PREFIX + "create_" + c)
            elif "fecha" in c.lower() or "date" in c.lower():
                values[c] = st.date_input(f"{c}", key=PREFIX + "create_" + c + "_date")
            elif "monto" in c.lower() or "precio" in c.lower() or "saldo" in c.lower() or "interes" in c.lower():
                values[c] = st.number_input(f"{c}", key=PREFIX + "create_" + c + "_num", format="%.2f")
            else:
                values[c] = st.text_input(f"{c}", key=PREFIX + "create_" + c)
        create_sub = st.form_submit_button("Crear")
        if create_sub:
            # construir INSERT
            insert_cols = []
            insert_vals = []
            params = []
            for k, v in values.items():
                # si el usuario dejó vacío la clave primaria la omitimos
                if (k.lower()=="id" or k.lower().startswith("id_")) and (v is None or str(v).strip()==""):
                    continue
                insert_cols.append(f"`{k}`")
                insert_vals.append("%s")
                # convertir date objects a string si aplica
                if hasattr(v, "isoformat"):
                    params.append(v.isoformat())
                else:
                    params.append(v)
            if not insert_cols:
                st.warning("No hay columnas para insertar.")
            else:
                q = f"INSERT INTO `{table}` (" + ", ".join(insert_cols) + ") VALUES (" + ", ".join(insert_vals) + ");"
                res = run_query(q, tuple(params), fetch=False)
                if res:
                    st.success("Registro creado. Refrescar página o ir a Listar.")
                else:
                    st.error("Error creando registro (revisa logs).")

    # FORM actualizar
    with st.expander("Actualizar / Eliminar", expanded=False):
        st.write("Busca por id o copia un registro desde la tabla superior y actualiza.")
        id_field = None
        # determinar primer campo id
        for c in cols:
            if c.lower()=="id" or c.lower().startswith("id_"):
                id_field = c
                break
        if not id_field:
            st.info("No se detectó campo id. No se puede activar edición por id.")
        else:
            id_to_edit = st.text_input("ID del registro a editar", key=PREFIX + "edit_id")
            if id_to_edit:
                row = run_query(f"SELECT * FROM `{table}` WHERE `{id_field}` = %s LIMIT 1;", (id_to_edit,), fetch=True)
                if row is None:
                    st.error("Error consultando registro.")
                elif not row:
                    st.warning("No se encontró el registro con ese id.")
                else:
                    record = row[0]
                    updated = {{}}
                    for c in cols:
                        if c==id_field:
                            st.write(f"{c}: {record.get(c)}")
                            updated[c] = record.get(c)
                        else:
                            # elegir tipo de input por heurística
                            val = record.get(c, "")
                            if isinstance(val, (int, float)):
                                updated[c] = st.number_input(f"{c}", value=val if val is not None else 0.0, key=PREFIX + "upd_" + c)
                            else:
                                updated[c] = st.text_input(f"{c}", value=str(val) if val is not None else "", key=PREFIX + "upd_" + c)
                    if st.button("Guardar cambios", key=PREFIX + "save_btn"):
                        # construir UPDATE
                        set_parts = []
                        params = []
                        for c in cols:
                            if c==id_field: 
                                continue
                            set_parts.append(f"`{c}` = %s")
                            params.append(updated[c])
                        params.append(updated[id_field])
                        q = f"UPDATE `{table}` SET " + ", ".join(set_parts) + f" WHERE `{id_field}` = %s;"
                        ok = run_query(q, tuple(params), fetch=False)
                        if ok:
                            st.success("Registro actualizado.")
                        else:
                            st.error("Error al actualizar.")
                    if st.button("Eliminar este registro", key=PREFIX + "del_btn"):
                        q = f"DELETE FROM `{table}` WHERE `{id_field}` = %s;"
                        ok = run_query(q, (updated[id_field],), fetch=False)
                        if ok:
                            st.success("Registro eliminado.")
                        else:
                            st.error("Error al eliminar.")
""")

# plantilla ESPECIAL para 'prestamo' con controles avanzados
prestamo_template = dedent("""
    # {filename}
    import streamlit as st
    from db import run_query

    st.set_page_config(layout="wide")
    PREFIX = "prestamo_"

    st.title("Préstamos — CRUD avanzado")
    st.write("Formulario con select de id existente, control de monto con +/- botones, interés en %, estado select y cálculo de total cuotas.")

    # LISTAR registros
    with st.expander("Listar préstamos", expanded=True):
        rows = run_query("SELECT * FROM prestamo ORDER BY id_prestamo DESC LIMIT 300;", fetch=True)
        if rows is None:
            st.error("Error listando préstamos.")
        else:
            st.dataframe(rows)

    # Crear nuevo o elegir existente
    with st.form(key=PREFIX + "form_create"):
        st.subheader("Crear nuevo préstamo / usar existente")
        # obtener ids existentes para elegir
        ids = run_query("SELECT id_prestamo FROM prestamo ORDER BY id_prestamo DESC LIMIT 200;", fetch=True)
        id_choices = [r['id_prestamo'] for r in ids] if ids else []
        selected_existing = st.selectbox("Seleccionar préstamo existente (opcional)", options=[""] + id_choices, key=PREFIX + "sel_existing")
        id_promotora = st.text_input("id_promotora", key=PREFIX + "id_promotora")
        id_ciclo = st.text_input("id_ciclo", key=PREFIX + "id_ciclo")
        id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")

        # monto con step y botones +/- (emulación)
        monto = st.number_input("Monto (USD)", min_value=0.0, step=0.01, key=PREFIX + "monto")
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            if st.button("+500", key=PREFIX + "add_500"):
                monto = monto + 500
        with col2:
            if st.button("-500", key=PREFIX + "sub_500"):
                monto = max(0, monto - 500)
        # interés como porcentaje
        interes = st.number_input("Interés (%)", min_value=0.0, max_value=100.0, step=0.1, key=PREFIX + "interes")
        saldo_restante = st.number_input("Saldo restante (USD)", min_value=0.0, step=0.01, key=PREFIX + "saldo")
        estado = st.selectbox("Estado", ["activo", "pagado", "moroso", "cancelado"], key=PREFIX + "estado")
        plazo = st.slider("Plazo (meses)", min_value=1, max_value=60, value=12, key=PREFIX + "plazo")
        # calcular total cuotas: simple ejemplo: (monto + monto*interes/100) / plazo
        total_cuotas = 0.0
        if plazo > 0:
            total_cuotas = round((monto + monto * interes / 100.0) / plazo, 2)
        st.markdown(f"**Total cuota estimada:** {total_cuotas} USD por mes")

        # crear o actualizar segun selected_existing
        submit = st.form_submit_button("Guardar préstamo")
        if submit:
            if selected_existing:
                # actualizar seleccionado
                q = \"\"\"UPDATE prestamo SET id_promotora=%s, id_ciclo=%s, id_miembro=%s, monto=%s,
                          intereses=%s, saldo_restante=%s, estado=%s, plazo_meses=%s, total_cuotas=%s
                          WHERE id_prestamo=%s;\"\"\"
                params = (id_promotora, id_ciclo, id_miembro, monto, interes, saldo_restante, estado, plazo, total_cuotas, selected_existing)
                ok = run_query(q, params, fetch=False)
                if ok:
                    st.success("Préstamo actualizado.")
                else:
                    st.error("Error actualizando préstamo.")
            else:
                # insertar nuevo
                q = \"\"\"INSERT INTO prestamo (id_promotora, id_ciclo, id_miembro, monto, intereses, saldo_restante, estado, plazo_meses, total_cuotas)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);\"\"\"
                params = (id_promotora, id_ciclo, id_miembro, monto, interes, saldo_restante, estado, plazo, total_cuotas)
                ok = run_query(q, params, fetch=False)
                if ok:
                    st.success("Préstamo creado.")
                else:
                    st.error("Error creando préstamo.")

    # eliminar
    with st.expander("Eliminar préstamo", expanded=False):
        id_del = st.text_input("ID a eliminar", key=PREFIX + "id_del")
        if st.button("Eliminar préstamo", key=PREFIX + "btn_del"):
            if id_del:
                ok = run_query("DELETE FROM prestamo WHERE id_prestamo = %s;", (id_del,), fetch=False)
                if ok:
                    st.success("Préstamo eliminado.")
                else:
                    st.error("Error al eliminar.")
            else:
                st.warning("Escribe un id para eliminar.")
""")

# función que crea archivo con template
def write_file(idx, table, readable, content):
    filename = f"{idx:02d}_{table}_crud.py"
    path = os.path.join(PAGES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.format(filename=filename, table=table, readable=readable))
    print("Wrote", path)

# generar archivos
for i, (table, readable) in enumerate(tables, start=1):
    if table == "prestamo":
        write_file(i, table, readable, prestamo_template)
    else:
        write_file(i, table, readable, crud_template)

print("Generación completada. Revisa la carpeta 'pages/'.")
