
---

# 3) `db.py`
```python
# db.py - conexión y helpers
import streamlit as st
import mysql.connector
from mysql.connector import Error

def get_db_config():
    # lee secrets en Streamlit Cloud o variables de entorno
    cfg = {
        "host": None, "user": None, "password": None, "database": None, "port": 3306
    }
    try:
        sec = st.secrets["db"]
        cfg["host"] = sec.get("host")
        cfg["user"] = sec.get("user")
        cfg["password"] = sec.get("password")
        cfg["database"] = sec.get("database")
        cfg["port"] = int(sec.get("port", 3306))
    except Exception:
        # intenta variables de entorno (opcional)
        import os
        cfg["host"] = os.getenv("DB_HOST")
        cfg["user"] = os.getenv("DB_USER")
        cfg["password"] = os.getenv("DB_PASS")
        cfg["database"] = os.getenv("DB_NAME")
        if os.getenv("DB_PORT"):
            cfg["port"] = int(os.getenv("DB_PORT"))
    return cfg

def get_connection():
    cfg = get_db_config()
    if not cfg["host"] or not cfg["user"]:
        return None
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            connection_timeout=10
        )
        return conn
    except Error as e:
        st.error(f"Error de conexión a la BD: {e}")
        return None

def test_connection():
    conn = get_connection()
    if not conn:
        return False, "No se pudo crear la conexión (revisa secrets)."
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True, "Conexión OK"
    except Exception as e:
        return False, str(e)

def run_query(query, params=None, fetch=True):
    """
    Ejecuta consulta SQL. params debe ser tupla/lista para parametrizar.
    fetch=True devuelve filas como lista de diccionarios.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            res = cursor.fetchall()
        else:
            conn.commit()
            res = True
        cursor.close()
        conn.close()
        return res
    except Exception as e:
        # muestra error (en producción loguea en archivo)
        st.error(f"Error en run_query(): {e}")
        return None

def get_table_names():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        st.error(f"Error listando tablas: {e}")
        return []
