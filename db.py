# db.py
"""
Funciones de conexión y utilidades para la base de datos MySQL.

Requisitos:
- mysql-connector-python
- pandas (opcional, para df_from_query)

Secrets esperados (en Streamlit Cloud -> Secrets):
[db]
host = "tu_host"
user = "tu_usuario"
password = "tu_password"
database = "tu_base"
port = "3306"   # opcional, por defecto 3306

NOTA: No pongas credenciales directamente en GitHub. Usa Streamlit Secrets.
"""

from typing import Optional, List, Any, Tuple, Dict
import os
import traceback

# Importamos streamlit solo dentro de funciones cuando sea necesario
try:
    import streamlit as st
except Exception:
    st = None

# mysql-connector
import mysql.connector
from mysql.connector import Error as MySQLError

# pandas es opcional pero muy útil
try:
    import pandas as pd
except Exception:
    pd = None


def _get_db_config_from_st_secrets() -> Dict[str, str]:
    """
    Intenta leer la configuración desde st.secrets['db'] (Streamlit Cloud).
    Si no existe, intenta leer variables de entorno:
    DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE, DB_PORT
    """
    cfg = {}
    # primero intentar streamlit secrets
    if st is not None:
        try:
            secrets = st.secrets
            if "db" in secrets:
                db = secrets["db"]
                cfg["host"] = db.get("host") or db.get("DB_HOST")
                cfg["user"] = db.get("user") or db.get("DB_USER")
                cfg["password"] = db.get("password") or db.get("DB_PASS") or db.get("DB_PASSWORD")
                cfg["database"] = db.get("database") or db.get("DB_NAME") or db.get("database")
                cfg["port"] = str(db.get("port", 3306))
                return cfg
        except Exception:
            # no hacemos crash aquí, intentamos env vars
            pass

    # fallback a variables de entorno
    cfg["host"] = os.environ.get("DB_HOST", os.environ.get("HOST", "localhost"))
    cfg["user"] = os.environ.get("DB_USER", os.environ.get("USER", ""))
    cfg["password"] = os.environ.get("DB_PASS", os.environ.get("DB_PASSWORD", ""))
    cfg["database"] = os.environ.get("DB_NAME", os.environ.get("DATABASE", ""))
    cfg["port"] = os.environ.get("DB_PORT", "3306")
    return cfg


def get_connection() -> Optional[mysql.connector.connection.MySQLConnection]:
    """
    Crea y devuelve una conexión a la base de datos MySQL usando mysql-connector.
    Devuelve None si no se pudo conectar.
    """
    cfg = _get_db_config_from_st_secrets()
    host = cfg.get("host")
    user = cfg.get("user")
    password = cfg.get("password")
    database = cfg.get("database")
    port = cfg.get("port", 3306)

    if not host or not user or not database:
        # Si estamos dentro de Streamlit, mostramos una guía
        if st is not None:
            st.error("Error de configuración de BD: revisa st.secrets['db'] o variables de entorno.")
        else:
            print("Error de configuración de BD: revisa variables de entorno o st.secrets['db'].")
        return None

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            autocommit=False,
            connection_timeout=10
        )
        return conn
    except MySQLError as e:
        msg = f"Error conectando a la BD: {e}"
        if st is not None:
            st.error(msg)
        else:
            print(msg)
        # para debugging también podemos imprimir traceback en logs
        traceback.print_exc()
        return None
    except Exception as e:
        if st is not None:
            st.error(f"Error inesperado conectando a la BD: {e}")
        else:
            print("Error inesperado conectando a la BD:", e)
        traceback.print_exc()
        return None


def close_connection(conn: Optional[mysql.connector.connection.MySQLConnection]) -> None:
    """Cierra la conexión si existe."""
    try:
        if conn:
            conn.close()
    except Exception:
        traceback.print_exc()


def get_table_names(conn: Optional[mysql.connector.connection.MySQLConnection] = None) -> List[str]:
    """
    Devuelve la lista de tablas de la BD.
    Si no se pasa conn, intenta crear una conexión temporal.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True

    tables: List[str] = []
    if conn is None:
        return tables

    try:
        cur = conn.cursor()
        cur.execute("SHOW TABLES;")
        rows = cur.fetchall()
        # rows vienen como tuplas: [('acta',), ('miembro',), ...]
        tables = [r[0] for r in rows]
        cur.close()
    except Exception:
        traceback.print_exc()
    finally:
        if own_conn:
            close_connection(conn)
    return tables


def fetch_all(query: str, params: Optional[Tuple[Any, ...]] = None,
              conn: Optional[mysql.connector.connection.MySQLConnection] = None) -> List[Tuple]:
    """
    Ejecuta SELECT y devuelve todas las filas como lista de tuplas.
    Si se pasa conn, lo usa; si no, crea uno temporal.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    if conn is None:
        return []

    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception:
        traceback.print_exc()
        return []
    finally:
        if own_conn:
            close_connection(conn)


def fetch_one(query: str, params: Optional[Tuple[Any, ...]] = None,
              conn: Optional[mysql.connector.connection.MySQLConnection] = None) -> Optional[Tuple]:
    """
    Ejecuta SELECT y devuelve la primera fila (tuple) o None.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    if conn is None:
        return None

    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        row = cur.fetchone()
        cur.close()
        return row
    except Exception:
        traceback.print_exc()
        return None
    finally:
        if own_conn:
            close_connection(conn)


def execute(query: str, params: Optional[Tuple[Any, ...]] = None,
            conn: Optional[mysql.connector.connection.MySQLConnection] = None, commit: bool = True) -> bool:
    """
    Ejecuta INSERT/UPDATE/DELETE. Devuelve True si se ejecutó correctamente.
    Si conn no se provee, crea uno temporal.
    """
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    if conn is None:
        return False

    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        if commit:
            conn.commit()
        cur.close()
        return True
    except Exception:
        traceback.print_exc()
        try:
            if conn is not None:
                conn.rollback()
        except Exception:
            pass
        return False
    finally:
        if own_conn:
            close_connection(conn)


def df_from_query(query: str, params: Optional[Tuple[Any, ...]] = None,
                  conn: Optional[mysql.connector.connection.MySQLConnection] = None) -> Optional["pd.DataFrame"]:
    """
    Ejecuta una query y devuelve un pandas.DataFrame (si pandas está instalado).
    """
    if pd is None:
        if st is not None:
            st.error("pandas no está instalado. Añade pandas a requirements.txt para usar df_from_query.")
        else:
            print("pandas no está instalado. Añade pandas para usar df_from_query.")
        return None

    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    if conn is None:
        return None

    try:
        df = pd.read_sql(query, con=conn, params=params or ())
        return df
    except Exception:
        traceback.print_exc()
        return None
    finally:
        if own_conn:
            close_connection(conn)


# ----------------------
# Métodos auxiliares para debug (no usados por defecto)
# ----------------------
def test_connection_print() -> None:
    """Prueba la conexión y muestra un mensaje por stdout/st.error si hay streamlit."""
    conn = get_connection()
    if conn:
        msg = "Conexión OK"
        if st is not None:
            st.success(msg)
        else:
            print(msg)
        close_connection(conn)
    else:
        msg = "No se pudo conectar a la BD"
        if st is not None:
            st.error(msg)
        else:
            print(msg)
