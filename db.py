import streamlit as st
import mysql.connector

# ----------------------------------------------------------
# 1) OBTENER CREDENCIALES DESDE STREAMLIT SECRETS
# ----------------------------------------------------------
def get_connection():
    """
    Crea y devuelve una conexión a MySQL usando los datos de st.secrets["db"].
    """
    try:
        db_config = {
            "host": st.secrets["db"]["host"],
            "user": st.secrets["db"]["user"],
            "password": st.secrets["db"]["password"],
            "database": st.secrets["db"]["database"],
            "port": st.secrets["db"].get("port", 3306)
        }

        return mysql.connector.connect(**db_config)

    except Exception as e:
        st.error(f"❌ Error conectando a la base de datos: {e}")
        return None


# ----------------------------------------------------------
# 2) FUNCIÓN GENÉRICA PARA EJECUTAR QUERIES
# ----------------------------------------------------------
def run_query(query, params=None, fetch=True):
    """
    Ejecuta una consulta SQL segura.
    - query: SQL a ejecutar
    - params: valores opcionales
    - fetch=True devuelve filas, False solo ejecuta INSERT/UPDATE/DELETE
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
        st.error(f"⚠ Error en run_query(): {e}")
        return None


# ----------------------------------------------------------
# 3) LISTAR TODAS LAS TABLAS DE LA BASE
# ----------------------------------------------------------
def get_table_names():
    """
    Devuelve una lista con los nombres de todas las tablas.
    """
    query = "SHOW TABLES;"
    result = run_query(query)

    if not result:
        return []

    # Cada resultado viene como {"Tables_in_nombreBD": "acta"}
    return [list(row.values())[0] for row in result]


# ----------------------------------------------------------
# 4) TEST DE CONEXIÓN (opcional pero útil)
# ----------------------------------------------------------
def test_connection():
    """
    Verifica si la conexión funciona.
    """
    try:
        conn = get_connection()
        if conn:
            conn.close()
            return True
        return False
    except:
        return False
