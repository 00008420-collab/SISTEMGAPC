import streamlit as st
import pymysql
from pymysql.cursors import DictCursor


# =====================================================
# 1. Obtener configuración desde st.secrets["mysql"]
# =====================================================
def get_mysql_config():
    """Lee la configuración MySQL desde Streamlit Secrets."""
    try:
        cfg = st.secrets["mysql"]
        return {
            "host": cfg.get("host"),
            "user": cfg.get("user"),
            "password": cfg.get("password"),
            "database": cfg.get("database"),
            "port": int(cfg.get("port", 3306)),
        }
    except Exception:
        st.error("❌ No se pudieron cargar los parámetros de la base de datos desde Secrets.")
        return None


# =====================================================
# 2. Crear conexión
# =====================================================
def get_connection():
    """Crea una conexión MySQL reutilizable."""
    cfg = get_mysql_config()

    if not cfg:
        return None

    try:
        conn = pymysql.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            cursorclass=DictCursor,
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error de conexión MySQL: {e}")
        return None


# =====================================================
# 3. Ejecutar consultas SELECT
# =====================================================
def run_query(query, params=None):
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        st.error(f"❌ Error ejecutando consulta: {e}")
        return None


# =====================================================
# 4. Ejecutar INSERT / UPDATE / DELETE
# =====================================================
def run_execute(query, params=None):
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
        conn.close()
        return True
    except Exception as e:
