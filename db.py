import streamlit as st
import mysql.connector
from mysql.connector import Error
import os

def get_db_config():
    try:
        s = st.secrets["db"]
        return {
            "host": s.get("host"),
            "user": s.get("user"),
            "password": s.get("password"),
            "database": s.get("database"),
            "port": int(s.get("port", 3306))
        }
    except Exception:
        return {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "database": os.getenv("DB_NAME"),
            "port": int(os.getenv("DB_PORT", 3306))
        }

def get_connection():
    cfg = get_db_config()
    if not cfg["host"] or not cfg["user"]:
        st.error("st.secrets['db'] no configurado o variables de entorno faltantes.")
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
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error probando BD: {e}")
        return False

def get_table_names():
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SHOW TABLES;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        st.error(f"Error listando tablas: {e}")
        return None

def run_query(query, params=None, fetch=True):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        if fetch:
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        else:
            conn.commit()
            cur.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Error en run_query(): {e}")
        return None
