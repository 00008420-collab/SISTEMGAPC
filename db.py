# db.py
import os
import streamlit as st
import mysql.connector
from mysql.connector import Error

def get_db_config():
    """
    Lee la configuración de conexión desde st.secrets['db'] o variables de entorno.
    En Streamlit Cloud: añade en Secrets (Settings -> Secrets) una sección 'db' con:
    host, user, password, database, port (opcional)
    Ejemplo (secrets.toml):
    [db]
    host = "mi-host"
    user = "mi-usuario"
    password = "mi-pass"
    database = "mi_db"
    port = 3306
    """
    # Intentar st.secrets['db']
    try:
        db_secret = st.secrets["db"]
        host = db_secret.get("host")
        user = db_secret.get("user")
        password = db_secret.get("password")
        database = db_secret.get("database")
        port = int(db_secret.get("port", 3306))
        return {"host": host, "user": user, "password": password, "database": database, "port": port}
    except Exception:
        # Intentar variables de entorno como fallback
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")
        port = int(os.getenv("DB_PORT", 3306))
        return {"host": host, "user": user, "password": password, "database": database, "port": port}

def get_connection():
    cfg = get_db_config()
    if not cfg["host"] or not cfg["user"] or not cfg["database"]:
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
        # no usar st.* aquí si quieres que la función sea utilizable fuera de streamlit
        # pero devolvemos None y el error arriba si se necesita
        return None

def test_connection():
    """
    Intenta conectarse y devuelve (True, mensaje) o (False, mensaje)
    """
    cfg = get_db_config()
    if not cfg["host"] or not cfg["user"] or not cfg["database"]:
        return False, "Falta configuración DB en secrets o variables de entorno."
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            connection_timeout=8
        )
        if conn and conn.is_connected():
            conn.close()
            return True, "Conexión OK"
        return False, "No se pudo establecer conexión"
    except Error as e:
        return False, f"Error conectando a la BD: {e}"

def get_table_names(schema=None):
    """
    Devuelve lista de tablas en la base de datos (names en minúscula).
    Si hay error devuelve [].
    """
    try:
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        # Si no pasaron schema, usar el actual de la conexión
        if not schema:
            schema = conn.database
        q = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type='BASE TABLE'
            ORDER BY table_name;
        """
        cursor.execute(q, (schema,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        tables = [r[0].lower() for r in rows]
        return tables
    except Exception:
        return []

def run_query(query, params=None, fetch=True):
    """
    Ejecuta una query segura. Si fetch=True retorna filas (lista de dicts).
    Si fetch=False hace commit y retorna True/False.
    """
    conn = get_connection()
    if not conn:
        # retornar None para identificar fallo de conexión
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
        # Si quieres ver el error en Streamlit: st.error(...)
        return None
