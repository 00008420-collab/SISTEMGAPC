# crud_template.py (plantilla - NO se importa en Streamlit; pegar y adaptar para cada Page)
import streamlit as st
from db import run_query
from auth_helpers import has_permission, require_permission, log_action, get_current_user

# CONFIG: editar para cada CRUD
TABLE = "NOMBRE_TABLA"         # reemplazar, e.g. "acta"
PK = "id_acta"                # pk de la tabla
FIELDS = [ "id_ciclo", "tipo", "fecha", "descripcion" ]  # campos (sin pk)
PAGE_PERMISSION_VIEW = "ver_" + TABLE   # convención opcional
PERM_CREATE = "crear_" + TABLE
PERM_UPDATE = "editar_" + TABLE
PERM_DELETE = "borrar_" + TABLE

def app():
    st.title("CRUD: " + TABLE.capitalize())

    usuario = get_current_user()

    # Lista: requiere permiso de 'view' o cualquier permiso para listar
    if not has_permission(PAGE_PERMISSION_VIEW):
        st.info("Acceso restringido: no tienes permiso de visualización.")
    else:
        rows = run_query(f"SELECT * FROM {TABLE} ORDER BY {PK} DESC LIMIT 500", fetch=True) or []
        st.dataframe(rows)

    st.markdown("---")

    # CREAR
    if has_permission(PERM_CREATE):
        with st.expander("Crear registro"):
            values = {}
            for f in FIELDS:
                values[f] = st.text_input(f"{f}", key=f"create_{f}")
            if st.button("Crear"):
                cols = ", ".join(FIELDS)
                ph = ", ".join(["%s"] * len(FIELDS))
                params = tuple(values[f] for f in FIELDS)
                q = f"INSERT INTO {TABLE} ({cols}) VALUES ({ph})"
                ok = run_query(q, params=params, fetch=False)
                if ok:
                    st.success("Registro creado.")
                    log_action(usuario, None, "create", TABLE, registro_id=None, detalle=str(values))
                else:
                    st.error("Error creando registro.")
    else:
        st.info("No tienes permiso para crear registros.")

    st.markdown("---")

    # ACTUALIZAR
    if has_permission(PERM_UPDATE):
        st.subheader("Actualizar / Eliminar")
        target = st.text_input("ID del registro a editar")
        if st.button("Cargar registro"):
            if target:
                row = run_query(f"SELECT * FROM {TABLE} WHERE {PK}=%s LIMIT 1", params=(target,), fetch=True)
                if row:
                    row = row[0]
                    edit_values = {}
                    for f in FIELDS:
                        edit_values[f] = st.text_input(f, value=str(row.get(f) or ""), key=f"edit_{f}")
                    if st.button("Guardar cambios"):
                        set_clause = ", ".join([f"{f}=%s" for f in FIELDS])
                        params = tuple(edit_values[f] for f in FIELDS) + (target,)
                        q = f"UPDATE {TABLE} SET {set_clause} WHERE {PK}=%s"
                        ok = run_query(q, params=params, fetch=False)
                        if ok:
                            st.success("Registro actualizado.")
                            log_action(usuario, None, "update", TABLE, registro_id=target, detalle=str(edit_values))
                        else:
                            st.error("Error actualizando.")
                    if st.button("Eliminar registro"):
                        ok = run_query(f"DELETE FROM {TABLE} WHERE {PK}=%s", params=(target,), fetch=False)
                        if ok:
                            st.success("Registro eliminado.")
                            log_action(usuario, None, "delete", TABLE, registro_id=target, detalle=None)
                        else:
                            st.error("Error eliminando.")
                else:
                    st.error("Registro no encontrado.")
            else:
                st.warning("Proporciona un ID.")
    else:
        st.info("No tienes permiso para editar/eliminar registros.")

# si sacas el app() para usar directamente, coloca una llamada o importa
