# crud_utils.py
from db import get_connection

def get_columns_from_db(table_name):
    if not table_name:
        return []
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{table_name}` LIMIT 1")
            # fetchone devuelve dict; las keys son las columnas (pymysql DictCursor)
            row = cur.fetchone()
            if row is None:
                # Si no hay filas, obtenemos columnas desde information_schema
                cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s", (table_name,))
                cols = [r[0] for r in cur.fetchall()]
                return cols
            else:
                return list(row.keys())
    except Exception:
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass
