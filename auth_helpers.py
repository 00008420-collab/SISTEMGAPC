# auth_helpers.py
import streamlit as st
from db import run_query
import socket

def get_current_user():
    """Devuelve username si está en session_state. """
    return st.session_state.get("user")

def load_permissions_for_current_user():
    """Carga permisos de DB en session_state['permissions'] si no están."""
    user = get_current_user()
    if not user:
        return []
    if "permissions" in st.session_state and st.session_state.get("user") == user:
        return st.session_state["permissions"]
    # obtener role_id
    row = run_query("SELECT id_role FROM users WHERE username=%s LIMIT 1", params=(user,), fetch=True)
    if not row:
        st.session_state["permissions"] = []
        return []
    role_id = row[0].get("id_role")
    perms = run_query("""
        SELECT p.code FROM permission p
        JOIN role_permission rp ON rp.permission_id = p.id_permission
        WHERE rp.role_id = %s
    """, params=(role_id,), fetch=True) or []
    codes = [r["code"] for r in perms]
    st.session_state["permissions"] = codes
    st.session_state["role_id"] = role_id
    return codes

def has_permission(permission_code):
    """Verdadero si el user actual tiene el permiso."""
    if "permissions" not in st.session_state:
        load_permissions_for_current_user()
    return permission_code in st.session_state.get("permissions", [])

def require_permission(permission_code):
    """Si no tiene permiso, muestra mensaje y detiene ejecución del Page (usa al inicio)."""
    if not has_permission(permission_code):
        st.warning("No tienes permiso para ver/ejecutar este módulo/acción.")
        st.stop()

def log_action(usuario, id_usuario, accion, tabla, registro_id=None, detalle=None):
    """Inserta una fila en audit_log (usa run_query con fetch=False)."""
    ip = None
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = None
    sql = """
        INSERT INTO audit_log (usuario, id_usuario, accion, tabla, registro_id, detalle, ip_origen)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    run_query(sql, params=(usuario, id_usuario, accion, tabla, str(registro_id), detalle, ip), fetch=False)
