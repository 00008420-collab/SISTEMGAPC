# db.py
import streamlit as st
import mysql.connector
from mysql.connector import errorcode

def _get_mysql_config():
    """
    Espera en Streamlit secrets:
    [mysql]
    host = "..."
    user = "..."
    password = "..."
    database = "..."
    port = 3306
    """
    cfg = st.secrets.get("mysql", {})
    # fallback: si no hay port, usar 3306
    cfg.setdefault("port", 3306)
    return cfg

def get_connection():
    cfg = _get_mysql_config()
    try:
        conn = mysql.connector.connect(
            host=cfg.get("host"),
            user=cfg.get("user"),
            password=cfg.get("password"),
            database=cfg.get("database"),
            port=int(cfg.get("port", 3306)),
            autocommit=False
        )
        return conn
    except mysql.connector.Error as err:
        # Mostrar error en streamlit de forma amigable
        if st._is_running_with_streamlit:
            st.error(f"Error de conexión a la BD: {err}")
        else:
            print(f"DB error: {err}")
        return None

def get_table_names():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SHOW TABLES")
        rows = cur.fetchall()
        # dependiendo del nombre de la columna (varía por MySQL)
        tables = []
        for r in rows:
            # r puede ser dict o tuple
            if isinstance(r, dict):
                tables.append(list(r.values())[0])
            elif isinstance(r, (list, tuple)):
                tables.append(r[0])
            else:
                tables.append(str(r))
        cur.close()
        conn.close()
        return tables
    except Exception as e:
        if st._is_running_with_streamlit:
            st.error(f"Error al listar tablas: {e}")
        return []
