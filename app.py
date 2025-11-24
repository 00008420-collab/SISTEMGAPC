# app.py (CORREGIDO)
import streamlit as st
from auth.login import login_user
from auth.config import check_login
from db import get_connection, get_table_names

st.set_page_config(page_title="SGAPC - Menú", layout="wide")

# Inicializar estado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = {}

# Mostrar formulario de login en sidebar si NO está logueado.
# Pero solo detener la ejecución si después de mostrar el formulario
# el usuario sigue sin iniciar sesión.
if not st.session_state.logged_in:
    login_user()
    # si después del formulario el usuario NO inició sesión, detenemos
    if not st.session_state.logged_in:
        st.stop()

# Si llegamos hasta aquí, el usuario está logueado
check_login()

# --- Prueba automática de conexión a la BD (añadir en app.py después de check_login()) ---
import streamlit as st
from db import get_connection, get_table_names

def test_db_connection(show_counts=False, max_tables=10):
    """
    Intentar conectar a la BD y mostrar resultados.
    - show_counts: si True, hace SELECT COUNT(*) por cada tabla (cuidado tablas grandes).
    - max_tables: límite de tablas a consultar si show_counts=True.
    """
    st.subheader("Verificación automática de la base de datos")

    conn = get_connection()
    if not conn:
        st.error("No se pudo establecer la conexión con la base de datos.")
        return

    try:
        st.success("Conexión establecida ✅")
        # Lista de tablas
        tablas = get_table_names()
        if not tablas:
            st.info("Conexión OK pero no se detectaron tablas en la base de datos.")
            return

        st.write(f"Se detectaron {len(tablas)} tablas:")
        # Mostrar la lista en un expander
        with st.expander("Ver tablas"):
            for t in tablas:
                st.write(f"- {t}")

        # Opcional: contar registros por tabla (desactivado por defecto; activar con show_counts=True)
        if show_counts:
            st.write("---")
            st.write(f"Conteo de registros (máx. {max_tables} tablas):")
            # limitar cantidad de tablas consultadas para evitar consultas largas
            tablas_para_contar = tablas[:max_tables]
            try:
                cur = conn.cursor()
                for t in tablas_para_contar:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM `{t}`")
                        cnt = cur.fetchone()[0]
                        st.write(f"`{t}` → {cnt} registros")
                    except Exception as e_table:
                        st.write(f"`{t}` → error contando registros: {e_table}")
                cur.close()
            except Exception as e_counts:
                st.write("No se pudieron obtener los conteos de tablas:", e_counts)

    except Exception as e:
        st.error(f"Error inesperado durante la verificación: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ---- Cómo se muestra en el menú/sidebar ----
with st.sidebar:
    st.markdown("### Herramientas")
    if st.button("Probar conexión a la BD ahora"):
        # Al pulsar el botón se ejecuta la prueba
        test_db_connection(show_counts=False)

# ---- Ejecutar la verificación automática al entrar (opcional) ----
# Si quieres que la comprobación se ejecute automáticamente cuando el usuario entra,
# descomenta la siguiente línea (sólo si no quieres que el usuario tenga que pulsar el botón).
# test_db_connection(show_counts=False)

st.title("📘 SGAPC - Menú")
st.write("Bienvenido al sistema. Usa el menú izquierdo (o Pages) para abrir los CRUDs.")

# --- Comprobación rápida de la BD (prueba visual) ---
st.header("Comprobación rápida de la base de datos")

conn = get_connection()
if conn:
    st.success("Conectado a la base de datos ✅")
    tablas = get_table_names()
    if tablas:
        st.write("Tablas detectadas:")
        st.write(", ".join(tablas))
    else:
        st.info("No se detectaron tablas (o la consulta devolvió vacío).")
    try:
        conn.close()
    except Exception:
        pass
else:
    st.error("No se pudo conectar a la base de datos. Revisa los secrets y credenciales.")
