import streamlit as st
import mysql.connector


def get_connection():
    """
    Crea y retorna una conexión a MySQL usando Streamlit Secrets.
    """
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
        st.error(f"❌ Error conectando a la base de datos: {e}")
        return None


def get_table_names():
    """
    Retorna una lista de todas las tablas en la base de datos.
    """
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    except Exception as e:
        st.error(f"❌ Error obteniendo tablas: {e}")
        return []
