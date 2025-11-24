import pymysql
import streamlit as st

def get_connection():
    try:
        conn = pymysql.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASS"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"]),
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        st.error(f"Error conectando a MySQL: {e}")
        return None
