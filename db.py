# db.py
import os
import mysql.connector
from mysql.connector import Error
import streamlit as st
from typing import Optional, List, Tuple, Any, Dict

# ---- Configuración de conexión ----
# Recomendación: en Streamlit Cloud usar st.secrets["db"]
# Estructura esperada en secrets.toml:
# [db]
# host = "tu_host"
# user = "tu_user"
# password = "tu_password"
# database = "tu_db"
# port = 3306

def _get_db_config_from_secrets() -> Dict[str, Any]:
    # Primero intenta st.secrets (Streamlit Cloud), luego variables de entorno
    cfg = {}
    if "db" in st.secrets:
        s = st.secrets["db"]
        cfg["host"] = s.get("host", "localhost")
        cfg["user"] = s.get("user", s.get("username", os.getenv("DB_USER")))
        cfg["password"] = s.get("password", os.getenv("DB_PASSWORD"))
        cfg["database"] = s.get("database", os.getenv("DB_NAME"))
        cfg["port"] = int(s.get("port", os.getenv("DB_PORT", 3306)))
    else:
        # fallback a env vars (útil en desarrollo)
        cfg["host"] = os.getenv("DB_HOST", "localhost")
        cfg["user"] = os.getenv("DB_USER", "root")
        cfg["password"] = os.getenv("DB_PASSWORD", "")
        cfg["database"] = os.getenv("DB_NAME", "")
        cfg["port"] = int(os.getenv("DB_PORT", 3306))
    return cfg

def get_connection() -> Optional[mysql.connector.connect]:
    cfg = _get_db_config_from_secrets()
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            charset="utf8mb4",
            use_unicode=True,
        )
        return conn
    except Error as e:
        # No mostrar credenciales, pero mostrar mensaje general
        st.error(f"Error conectando a la BD: {e}")
        return None

# Test de conexión: devuelve (True, mensaje) o (False, mensaje)
def test_connection() -> Tuple[bool, str]:
    conn = get_connection()
    if not conn:
        return False, "No se pudo abrir conexión (credenciales / host)."
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True, "Conexión OK"
    except Exception as e:
        return False, f"Error al ejecutar test_connection(): {e}"

# Ejecutar query segura (params -> tuple)
def run_query(query: str, params: Optional[Tuple]=None, fetch: bool=True):
    """
    Ejecuta una consulta SQL segura.
    - query: SQL a ejecutar
    - params: valores opcionales (tuple o list)
    - fetch=True devuelve filas (list of dicts), False solo ejecuta INSERT/UPDATE/DELETE y devuelve True/False
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = True
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        # Registrar / mostrar error de forma amigable
        st.error(f"Error en run_query(): {e}")
        return None

def get_table_names() -> Optional[List[str]]:
    """
    Devuelve la lista de tablas detectadas en la BD (lowercase).
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # rows es lista de tuplas, por ejemplo [('acta',), ('miembro',)]
        tables = [r[0] for r in rows]
        return tables
    except Exception as e:
        st.error(f"Error al listar tablas: {e}")
        return None

# Helpers para trabajar con users / roles (según tu esquema en phpmyadmin)
def get_user_by_username(username: str):
    q = "SELECT * FROM users WHERE username = %s LIMIT 1"
    res = run_query(q, (username,), fetch=True)
    if res:
        return res[0]
    return None

def get_role_permissions_by_role(role_name: str):
    """
    Asume que existe una tabla role_permission o similar.
    Devuelve lista de nombres de tabla permitidas para el role.
    """
    q = """
    SELECT rp.table_name
    FROM role_permission rp
    JOIN role r ON r.id_role = rp.role
    WHERE r.name = %s
    """
    res = run_query(q, (role_name,), fetch=True)
    if res is None:
        return []
    return [r["table_name"] for r in res]

# FIN db.py
