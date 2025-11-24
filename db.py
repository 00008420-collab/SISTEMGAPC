# db.py
import os
import streamlit as st
import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Conecta usando Streamlit secrets si está en Cloud,
    o variables de entorno, o defaults locales.
    """
    # Intentar secrets (Streamlit Cloud)
    host = os.getenv("DB_HOST") or (st.secrets["db"]["host"] if "db" in st.secrets else None)
    user = os.getenv("DB_USER") or (st.secrets["db"]["user"] if "db" in st.secrets else None)
    password = os.getenv("DB_PASS") or (st.secrets["db"]["password"] if "db" in st.secrets else None)
    database = os.getenv("DB_NAME") or (st.secrets["db"]["database"] if "db" in st.secrets else None)
    port = os.getenv("DB_PORT") or (st.secrets["db"].get("port") if "db" in st.secrets else 3306)

    if not host or not user or not database:
        st.error("DB no configurada. Revisa secrets o variables de entorno.")
        return None

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port)
        )
        return conn
    except Error as e:
        st.error(f"Error de conexión a la BD: {e}")
        return None

def run_query(query, params=None, fetch=True):
    """
    Ejecuta una consulta SQL segura usando placeholders.
    - query: SQL con %s placeholders
    - params: tuple/list de parámetros
    - fetch: True -> devuelve filas (list of dicts), False -> ejecuta y commitea
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
        # en Cloud los errores se muestran en logs; aquí mostramos algo en UI
        st.error(f"Error en run_query(): {e}")
        return None

def test_connection():
    conn = get_connection()
    if not conn:
        return False
    try:
        conn.close()
        return True
    except:
        return False

def get_table_names():
    rows = run_query("SHOW TABLES", fetch=True)
    if not rows:
        return []
    # mysql returns list of dicts with varying key name: get the first value of each row
    names = []
    for r in rows:
        if isinstance(r, dict):
            vals = list(r.values())
            if vals:
                names.append(vals[0])
    return names
