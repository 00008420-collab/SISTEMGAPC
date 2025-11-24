# db.py
import streamlit as st
import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Lee credenciales desde st.secrets['db'] y devuelve una conexión MySQL.
    """
    try:
        cfg = st.secrets["db"]
    except Exception as e:
        st.error("st.secrets['db'] no está configurado. Añade tus credenciales en Secrets.")
        return None

    try:
        conn = mysql.connector.connect(
            host=cfg.get("host"),
            user=cfg.get("user"),
            password=cfg.get("password"),
            database=cfg.get("database"),
            port=int(cfg.get("port", 3306))
        )
        return conn
    except Error as e:
        st.error(f"Error conectando a la BD: {e}")
        return None

def run_query(query: str, params: tuple = None, fetch: bool = True):
    """
    Ejecuta consulta segura. Retorna filas (list[dict]) si fetch=True, True si sin fetch (commit), None en error.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        # no usar st.error en librerías reutilizables normalmente, pero para debug en Streamlit es útil
        st.error(f"Error en run_query(): {e}")
        return None

def test_connection():
    """
    Retorna (True, mensaje) si ok, (False, mensaje) si error.
    """
    conn = get_connection()
    if not conn:
        return False, "No se pudo crear conexión (secrets faltantes o incorrectos)."
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchall()
        cursor.close()
        conn.close()
        return True, "Conexión OK"
    except Exception as e:
        return False, str(e)

def get_table_names():
    """
    Devuelve lista de nombres de tablas en la BD o [] si error.
    """
    q = "SHOW TABLES;"
    rows = run_query(q, fetch=True)
    if rows is None:
        return []
    # cuando cursor.dictionary=True, cada fila es { 'Tables_in_dbname': 'table' }
    tables = []
    if rows:
        # manejar clave indeterminada: tomar el primer valor de cada row
        for r in rows:
            if isinstance(r, dict) and r:
                tables.append(list(r.values())[0])
            else:
                # si viene como tupla
                tables.append(r[0])
    return tables

def get_role_permissions_from_db():
    """
    Intenta leer la tabla role_permission (columns: role, table_name).
    Retorna dict: { role_name: [table1, table2, ...], ... }
    Si no existe o error, retorna {}.
    """
    # check table exists:
    try:
        rows = run_query("SHOW TABLES LIKE 'role_permission';", fetch=True)
        if not rows:
            return {}
    except Exception:
        return {}

    # read permissions
    rows = run_query("SELECT role, table_name FROM role_permission;", fetch=True)
    if not rows:
        return {}
    perms = {}
    for r in rows:
        role = r.get("role") or r.get("role_name") or r.get("role")
        table = r.get("table_name")
        if not role or not table:
            continue
        perms.setdefault(role, []).append(table)
    return perms
