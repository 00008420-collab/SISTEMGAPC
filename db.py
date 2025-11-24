import streamlit as st
import mysql.connector

# -----------------------------
# 1. Conexión a la BD
# -----------------------------
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["db"]["host"],
            user=st.secrets["db"]["user"],
            password=st.secrets["db"]["password"],
            database=st.secrets["db"]["database"],
            port=st.secrets["db"]["port"]
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error conectando a la BD: {e}")
        return None


# -----------------------------
# 2. Probar conexión
# -----------------------------
def test_connection():
    conn = get_connection()
    if conn:
        conn.close()
        return True
    return False


# -----------------------------
# 3. Obtener nombres de tablas
# -----------------------------
def get_table_names():
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        st.error(f"Error obteniendo tablas: {e}")
        return None


# -----------------------------
# 4. Ejecutar query genérico
# -----------------------------
def run_query(query, params=None, fetch=True):
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
        st.error(f"Error en run_query(): {e}")
        return None
