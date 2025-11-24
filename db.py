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
        # Mostrar error de forma segura en Streamlit (sin usar atributos privados)
        try:
            st.error(f"Error de conexión a la BD: {err}")
        except Exception:
            # En caso raro de no poder usar st.error, imprimirlo por consola
            print(f"Error de conexión a la BD: {err}")
        return None

def get_table_names():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SHOW TABLES")
        rows = cur.fetchall()
        tablas = []
        for r in rows:
            if isinstance(r, dict):
                tablas.append(list(r.values())[0])
            elif isinstance(r, (list, tuple)):
                tablas.append(r[0])
            else:
                tablas.append(str(r))
        cur.close()
        conn.close()
        return tablas
    except Exception as e:
        try:
            st.error(f"Error al listar tablas: {e}")
        except Exception:
            print(f"Error al listar tablas: {e}")
        return []
