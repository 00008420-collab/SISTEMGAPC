# db.py
import streamlit as st
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

# Lee credenciales desde st.secrets
def _get_db_config():
    try:
        cfg = st.secrets["db"]
        return {
            "host": cfg.get("host"),
            "user": cfg.get("user"),
            "password": cfg.get("password"),
            "database": cfg.get("database"),
            "port": int(cfg.get("port", 3306))
        }
    except Exception:
        # Si no hay secrets, intenta variables de entorno por compatibilidad
        return None

@contextmanager
def get_connection():
    """
    Context manager que devuelve un objeto de conexión.
    Uso:
        with get_connection() as conn:
            cursor = conn.cursor()
            ...
    """
    cfg = _get_db_config()
    if not cfg:
        raise RuntimeError("No DB config found. Set st.secrets['db']")
    conn = None
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            autocommit=True
        )
        yield conn
    except Error as e:
        # reenviar excepcion para que la UI la muestre
        raise e
    finally:
        if conn and conn.is_connected():
            conn.close()

def run_query(query, params=None, fetch=False):
    """Ejecuta una consulta. Si fetch True, devuelve lista de tuplas o diccionarios según fetchall"""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            rows = cursor.fetchall()
            cursor.close()
            return rows
        else:
            cursor.close()
            return None

def get_table_names():
    """Devuelve lista de tablas en la BD"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        rows = cursor.fetchall()
        cursor.close()
        # rows es lista de tuplas, tomar primer elemento de cada tupla
        return [r[0] for r in rows]
