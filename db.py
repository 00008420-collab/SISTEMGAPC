# db.py
import os
import streamlit as st

try:
    import mysql.connector
    from mysql.connector import Error
except Exception as e:
    # En despliegue en Streamlit Cloud, si falta el paquete, el logs lo mostrarán.
    raise

def _read_db_config():
    """
    Lee credenciales desde st.secrets['db'] si existe, 
    o desde variables de entorno DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT.
    """
    host = port = user = password = database = None

    # Preferir st.secrets (Streamlit Cloud)
    if hasattr(st, "secrets") and st.secrets is not None:
        dbsec = st.secrets.get("db") or st.secrets
        host = dbsec.get("DB_HOST") or dbsec.get("host") or dbsec.get("db_host")
        user = dbsec.get("DB_USER") or dbsec.get("user")
        password = dbsec.get("DB_PASS") or dbsec.get("password")
        database = dbsec.get("DB_NAME") or dbsec.get("database")
        port = dbsec.get("DB_PORT") or dbsec.get("port")
    # Fallback a variables de entorno
    host = host or os.environ.get("DB_HOST")
    user = user or os.environ.get("DB_USER")
    password = password or os.environ.get("DB_PASS")
    database = database or os.environ.get("DB_NAME")
    port = port or os.environ.get("DB_PORT") or 3306

    return {
        "host": host,
        "user": user,
        "password": password,
        "database": database,
        "port": int(port) if port else 3306,
    }

def get_connection():
    """
    Intenta devolver una conexión mysql.connector.
    Retorna la conexión (object) o None en caso de error.
    """
    cfg = _read_db_config()
    if not cfg["host"] or not cfg["user"] or not cfg["database"]:
        return None

    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            connection_timeout=5
        )
        return conn
    except Error as e:
        # No usar st.error aquí porque pueden llamarlo desde fuera,
        # se devuelve None y el caller puede mostrar el error.
        return None

def test_connection():
    """
    Devuelve siempre una tupla (ok: bool, message: str)
    """
    cfg = _read_db_config()
    if not cfg["host"] or not cfg["user"] or not cfg["database"]:
        return False, "Faltan credenciales (DB_HOST/DB_USER/DB_NAME). Añade st.secrets o variables de entorno."

    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            connection_timeout=5
        )
        if conn and conn.is_connected():
            conn.close()
            return True, "Conexión OK"
        else:
            return False, "No se pudo conectar (conexión no establecida)."
    except Error as e:
        return False, f"Error conectando a la BD: {e}"

def get_table_names():
    """
    Devuelve lista de tablas (strings) o None en caso de error.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SHOW TABLES;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # rows come as tuples like [('acta',), ('miembro',)]
        return [r[0] for r in rows]
    except Exception as e:
        return None

def run_query(query, params=None, fetch=True):
    """
    Ejecuta una consulta SQL segura.
    - query: SQL a ejecutar
    - params: valores opcionales (tuple/list)
    - fetch=True devuelve filas, False solo ejecuta INSERT/UPDATE/DELETE
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)  # retorna dicts
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
        # En app principal ya mostramos errores a usuario, aquí devolvemos None
        return None
