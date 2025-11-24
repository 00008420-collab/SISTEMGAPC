# db.py
import streamlit as st
import mysql.connector
from mysql.connector import Error

def get_connection():
    """
    Lee st.secrets['db'] y devuelve una conexión mysql.connector.
    En Streamlit Cloud: agrega secrets -> db: {host, user, password, database, port}
    """
    if "db" not in st.secrets:
        st.error("st.secrets no contiene la clave 'db'. Añádela en Settings > Secrets.")
        return None
    cfg = st.secrets["db"]
    try:
        conn = mysql.connector.connect(
            host=cfg.get("host", "localhost"),
            user=cfg.get("user"),
            password=cfg.get("password"),
            database=cfg.get("database"),
            port=int(cfg.get("port", 3306))
        )
        return conn
    except Exception as e:
        st.error(f"Error conectando a la BD: {e}")
        return None

def run_query(query, params=None, fetch=True):
    """
    Ejecuta una consulta SQL segura.
    - query: SQL (con %s para parámetros)
    - params: tuple/list or None
    - fetch=True devuelve filas (list of dict), False hace commit y devuelve True/False
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
        # No usar st.exception que filtra info en cloud; usar st.error para mostrar texto.
        st.error(f"Error en run_query(): {e}")
        return None
