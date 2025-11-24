# db.py
"""
Módulo de acceso a la base de datos (MySQL) usando pymysql.
Funciones públicas principales:
- get_connection()
- test_connection() -> (bool, message)
- get_table_names() -> list[str]
- run_query(query, params=None, fetch=True) -> list[dict] | bool | None

Lee credenciales desde:
- streamlit secrets: st.secrets["db"] (si existe)
  formato recomendado en secrets.toml:
    [db]
    host = "tu_host"
    user = "tu_user"
    password = "tu_password"
    database = "tu_database"
    port = 3306

- o variables de entorno: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
"""

from typing import Optional, Tuple, Any, List, Dict
import os
import pymysql
import pymysql.cursors
import traceback

def _get_config_from_st_secrets() -> Optional[dict]:
    """
    Intenta leer st.secrets['db'] si se está ejecutando bajo Streamlit y secrets existe.
    No importamos streamlit en el top-level para evitar efectos secundarios en import.
    """
    try:
        import streamlit as st  # import local y controlado
    except Exception:
        return None

    db = st.secrets.get("db") if hasattr(st, "secrets") else None
    if isinstance(db, dict):
        return db
    return None

def get_db_config() -> dict:
    """
    Devuelve diccionario con keys: host, user, password, database, port
    Busca en este orden:
      1) st.secrets["db"] si está disponible
      2) variables de entorno DB_*
    Lanzará ValueError si faltan parámetros esenciales.
    """
    cfg = _get_config_from_st_secrets()
    if not cfg:
        # leer variables de entorno
        cfg = {
            "host": os.environ.get("DB_HOST", "localhost"),
            "user": os.environ.get("DB_USER", os.environ.get("MYSQL_USER", None)),
            "password": os.environ.get("DB_PASSWORD", os.environ.get("MYSQL_PASSWORD", None)),
            "database": os.environ.get("DB_NAME", os.environ.get("MYSQL_DATABASE", None)),
            "port": int(os.environ.get("DB_PORT", os.environ.get("MYSQL_PORT", 3306))),
        }

    # validar
    required = ["host", "user", "password", "database"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        raise ValueError(f"Faltan credenciales DB: {', '.join(missing)}. Añádelas a streamlit secrets o variables de entorno.")
    # asegurar puerto como int
    try:
        cfg["port"] = int(cfg.get("port", 3306))
    except Exception:
        cfg["port"] = 3306

    return cfg

def get_connection():
    """
    Devuelve una conexión pymysql (cursor dict) o lanza excepción si falla.
    IMPORTANTE: caller debe cerrar la conexión (conn.close()) o usar run_query que la cierre.
    """
    cfg = get_db_config()
    conn = pymysql.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg["port"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        charset="utf8mb4",
    )
    return conn

def test_connection(timeout_seconds: int = 5) -> Tuple[bool, str]:
    """
    Intenta conectar y ejecutar una consulta ligera.
    Retorna (True, "OK") si todo bien, o (False, "mensaje de error").
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            conn.close()
            return True, "Conexión OK"
        except Exception as e:
            try:
                conn.close()
            except Exception:
                pass
            tb = traceback.format_exc()
            return False, f"Error ejecutando prueba simple: {e}\n{tb}"
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Error conectando a la BD: {e}\n{tb}"

def get_table_names() -> List[str]:
    """
    Devuelve lista de tablas (strings). En caso de error devuelve [].
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Usar SHOW FULL TABLES si quieres tipo, o SHOW TABLES simple
                cur.execute("SHOW TABLES;")
                rows = cur.fetchall()
            conn.close()
            # rows será lista de dicts con una sola key (nombre dinámico). Extraer valores.
            table_names = []
            for r in rows:
                # r puede ser {'Tables_in_dbname': 'table'}
                vals = list(r.values())
                if vals:
                    table_names.append(str(vals[0]))
            return table_names
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            return []
    except Exception:
        return []

def run_query(query: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[Any]:
    """
    Ejecuta una consulta SQL segura.
    - query: SQL con %s para parámetros
    - params: tupla de parámetros o None
    - fetch: True => devuelve lista de dicts (fetchall); False => realiza commit y devuelve True/False.
    En errores devuelve None.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                result = cur.fetchall()
            else:
                conn.commit()
                result = True
        conn.close()
        return result
    except Exception as e:
        # asegurar cierre de conexión si ocurrió
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        # puedes loggear el error con print() (aparece en logs de Streamlit Cloud)
        print(f"[db.run_query] Error: {e}")
        print(traceback.format_exc())
        return None
