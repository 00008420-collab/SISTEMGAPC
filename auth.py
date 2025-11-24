# auth.py
from db import run_query, get_table_names
import streamlit as st

def load_permissions_for_role(role_id):
    """Devuelve lista de códigos de permiso para el role_id"""
    if not role_id:
        return []
    q = """
    SELECT p.code FROM permission p
    JOIN role_permission rp ON rp.permission_id = p.id_permission
    WHERE rp.role_id = %s
    """
    rows = run_query(q, params=(role_id,), fetch=True)
    return [r["code"] for r in rows] if rows else []

def get_user_role_id(username):
    q = "SELECT id_user, id_role FROM users WHERE username = %s LIMIT 1"
    rows = run_query(q, params=(username,), fetch=True)
    if rows:
        return rows[0].get("id_role")
    return None

def user_has_permission(username, permission_code):
    """Comprueba permiso consultando sesión si está cargada, sino consulta DB."""
    if "permissions" in st.session_state and st.session_state.get("user") == username:
        return permission_code in st.session_state.get("permissions", [])
    role_id = get_user_role_id(username)
    if not role_id:
        return False
    perms = load_permissions_for_role(role_id)
    return permission_code in perms
