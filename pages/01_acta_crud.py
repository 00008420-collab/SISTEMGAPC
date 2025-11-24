# pages/01_acta_crud.py
import streamlit as st
from db import run_query
from auth_helpers import has_permission, log_action, get_current_user

TABLE = "acta"
PK = "id_acta"
FIELDS = ["id_ciclo", "tipo", "fecha", "descripcion"]
PERM_CREATE = "crear_acta"
PERM_VIEW = "ver_acta"
PERM_UPDATE = "editar_acta"
PERM_DELETE = "borrar_acta"

def app():
    st.title("Actas")

    usuario = get_current_user()

    # LISTAR
    if has_permission(PERM_VIEW):
        rows = run_query(f"SELECT * FROM {TABLE} ORDER BY {PK} DESC LIMIT 500", fetch=True) or []
        st.dataframe(rows)
    else:
        st.warning("No tienes permiso para ver actas.")

    st.markdown("---")

    # CREAR
    if has_permission(PERM_CREATE):
        with st.form("crear_acta"):
            id_ciclo = st.text_input("id_ciclo")
            tipo = st.text_input("tipo")
            fecha = st.date_input("fecha")
            descripcion = st.text_area("descripcion")
            if st.form_submit_button("Crear acta"):
                q = f"INSERT INTO {TABLE} (id_ciclo, tipo, fecha, descripcion) VALUES (%s, %s, %s, %s)"
                params = (id_ciclo, tipo, fecha.strftime("%Y-%m-%d"), descripcion)
                ok = run_query(q, params=params, fetch=False)
                if ok:
                    st.success("Acta creada.")
                    log_action(usuario, None, "create", TABLE, registro_id=None, detalle=str(params))
                else:
                    st.error("Error creando acta.")
    else:
        st.info("No tienes permiso para crear actas.")

    st.markdown("---")

    # EDITAR / BORRAR
    if has_permission(PERM_UPDATE) or has_permission(PERM_DELETE):
        id_target = st.text_input("ID acta a editar/eliminar")
        if st.button("Cargar acta"):
            if id_target:
                row = run_query(f"SELECT * FROM {TABLE} WHERE {PK}=%s LIMIT 1", params=(id_target,), fetch=True)
                if row:
                    row = row[0]
                    new_tipo = st.text_input("tipo", value=row.get("tipo",""))
                    new_fecha = st.date_input("fecha", value=row.get("fecha"))
                    new_descripcion = st.text_area("descripcion", value=row.get("descripcion",""))
                    if st.button("Guardar cambios"):
                        q = f"UPDATE {TABLE} SET tipo=%s, fecha=%s, descripcion=%s WHERE {PK}=%s"
                        params = (new_tipo, new_fecha.strftime("%Y-%m-%d"), new_descripcion, id_target)
                        ok = run_query(q, params=params, fetch=False)
                        if ok:
                            st.success("Acta actualizada.")
                            log_action(usuario, None, "update", TABLE, registro_id=id_target, detalle=str(params))
                        else:
                            st.error("Error actualizando.")
                    if st.button("Eliminar acta"):
                        ok = run_query(f"DELETE FROM {TABLE} WHERE {PK}=%s", params=(id_target,), fetch=False)
                        if ok:
                            st.success("Acta eliminada.")
                            log_action(usuario, None, "delete", TABLE, registro_id=id_target, detalle=None)
                        else:
                            st.error("Error eliminando.")
                else:
                    st.error("Acta no encontrada.")
            else:
                st.warning("Introduce ID.")
    else:
        st.info("No tienes permiso para editar o eliminar actas.")
