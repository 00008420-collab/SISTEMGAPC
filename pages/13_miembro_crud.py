# pages/13_miembro_crud.py
import streamlit as st
from db import run_query
from auth_helpers import has_permission, log_action, get_current_user, load_permissions_for_current_user

TABLE = "miembro"
PK = "id_miembro"
FIELDS = ["id_tipo_usuario", "apellido", "dui", "direccion"]
PERM_CREATE = "alta_usuario"
PERM_VIEW = "ver_miembro"
PERM_UPDATE = "editar_miembro"
PERM_DELETE = "borrar_miembro"

def get_miembro_id_for_user(username):
    # si existe mapeo entre users.username y miembro (por ejemplo users.id_user = miembro.id_miembro)
    row = run_query("SELECT id_user FROM users WHERE username=%s LIMIT 1", params=(username,), fetch=True)
    if not row:
        return None
    id_user = row[0].get("id_user")
    # Buscar miembro con id_tipo_usuario = id_user o con campo que haga relación; ajusta según tu esquema
    row2 = run_query("SELECT id_miembro FROM miembro WHERE id_miembro = %s LIMIT 1", params=(id_user,), fetch=True)
    if row2:
        return row2[0].get("id_miembro")
    return None

def app():
    st.title("Miembros")

    user = get_current_user()
    load_permissions_for_current_user()

    # LISTAR
    if has_permission(PERM_VIEW):
        rows = run_query(f"SELECT * FROM {TABLE} ORDER BY {PK} DESC LIMIT 500", fetch=True) or []
        st.dataframe(rows)
    else:
        st.info("No tienes permiso para ver miembros.")

    st.markdown("---")
    # CREAR
    if has_permission(PERM_CREATE):
        with st.form("crear_miembro"):
            id_tipo = st.number_input("id_tipo_usuario", value=1, step=1)
            apellido = st.text_input("apellido")
            dui = st.text_input("dui")
            direccion = st.text_input("direccion")
            if st.form_submit_button("Crear miembro"):
                q = f"INSERT INTO {TABLE} (id_tipo_usuario, apellido, dui, direccion) VALUES (%s, %s, %s, %s)"
                params = (id_tipo, apellido, dui, direccion)
                ok = run_query(q, params=params, fetch=False)
                if ok:
                    st.success("Miembro creado.")
                    log_action(user, None, "create", TABLE, registro_id=None, detalle=str(params))
                else:
                    st.error("Error creando miembro.")
    else:
        st.info("No tienes permiso para crear miembros.")

    st.markdown("---")
    # EDITAR PROPIO REGISTRO (miembro normal)
    member_id = st.text_input("ID miembro (para editar)")
    if member_id:
        # si el usuario no es admin, solo puede editar su propio miembro
        if not has_permission("administrador") and not has_permission("editar_miembro"):
            # intentar mapear usuario->miembro
            my_id = get_miembro_id_for_user(user)
            if str(my_id) != str(member_id):
                st.warning("No puedes editar el registro de otro miembro.")
            else:
                pass  # se permite
        # cargar registro
        row = run_query(f"SELECT * FROM {TABLE} WHERE {PK}=%s", params=(member_id,), fetch=True)
        if row:
            row = row[0]
            new_apellido = st.text_input("apellido", value=row.get("apellido",""))
            new_dui = st.text_input("dui", value=row.get("dui",""))
            new_direccion = st.text_input("direccion", value=row.get("direccion",""))
            if st.button("Guardar cambios"):
                q = f"UPDATE {TABLE} SET apellido=%s, dui=%s, direccion=%s WHERE {PK}=%s"
                params = (new_apellido, new_dui, new_direccion, member_id)
                ok = run_query(q, params=params, fetch=False)
                if ok:
                    st.success("Miembro actualizado.")
                    log_action(user, None, "update", TABLE, registro_id=member_id, detalle=str(params))
                else:
                    st.error("Error actualizando.")
        else:
            st.info("Registro no encontrado.")
