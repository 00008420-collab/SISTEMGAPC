# app.py
import streamlit as st
from typing import List

st.set_page_config(page_title="SGAPC - Menú principal", layout="wide")

# --- Try to import db helpers (must exist in your repo) ---
try:
    from db import test_connection, get_table_names, run_query
except Exception as e:
    # If db.py is missing or doesn't define the functions we expect, show a clear error
    st.write("Error al importar funciones de db.py:", e)
    st.stop()


# --- Try to import your auth module (optional) ---
auth_available = False
try:
    # Se espera que auth/login.py tenga funciones: login_box(), require_login(), logout_user() u otras.
    from auth.login import login_box, require_login, logout_user, get_current_user  # optional
    auth_available = True
except Exception:
    # No hay módulo de auth (fallback más abajo)
    auth_available = False


# ---------- Authentication helpers (fallback) ----------
def fallback_login_form():
    """
    Formulario muy simple para pruebas cuando no existan los helpers de auth.
    **No es seguro** para producción. Si tienes auth/login, preferir usarlo.
    """
    st.sidebar.subheader("Iniciar sesión (modo prueba)")
    username = st.sidebar.text_input("Usuario", key="fallback_user")
    submitted = st.sidebar.button("Iniciar sesión (prueba)")
    if submitted and username:
        st.session_state["user"] = {"username": username, "display_name": username}
        st.sidebar.success(f"Conectado como: {username}")
        return True
    return False


def require_login_local():
    """
    Requiere inicio de sesión. Si auth_available usa ese; si no, usa fallback.
    Devuelve el objeto usuario (dict) o None.
    """
    # Si ya está en sesión
    if st.session_state.get("user"):
        return st.session_state["user"]

    if auth_available:
        # Llamamos a require_login() del módulo auth si lo provees
        try:
            user = require_login()
            if user:
                st.session_state["user"] = user
                return user
            return None
        except Exception as e:
            st.warning("Error al usar auth.require_login(): se usará fallback. (" + str(e) + ")")
            return None
    else:
        # Mostrar fallback en la barra lateral
        ok = fallback_login_form()
        if ok:
            return st.session_state.get("user")
        return None


# ---------- Small UI helpers ----------
def show_connection_status():
    """Comprueba la conexión y muestra resultado."""
    try:
        result = test_connection()
        # test_connection puede devolver bool o (bool,msg)
        if isinstance(result, tuple) and len(result) >= 1:
            ok = result[0]
            msg = result[1] if len(result) > 1 else ""
        else:
            ok = bool(result)
            msg = "Conexión OK" if ok else "Error desconocido"

        if ok:
            st.success("Conexión establecida ✅ — " + str(msg))
            return True
        else:
            st.error("Error de conexión a la BD: " + str(msg))
            return False
    except Exception as e:
        st.error("Error al ejecutar test_connection(): " + str(e))
        return False


def safe_get_tables() -> List[str]:
    """Obtiene la lista de tablas desde db.get_table_names(), devuelve lista vacía en error."""
    try:
        tbls = get_table_names()
        if tbls is None:
            return []
        # Garantizar lista de strings
        return [t for t in tbls if isinstance(t, str)]
    except Exception as e:
        st.warning("No fue posible listar tablas (get_table_names falló): " + str(e))
        return []


def show_table_data(table_name: str):
    """Muestra las primeras filas de la tabla seleccionada (limit 100)."""
    if not table_name:
        st.info("Selecciona una tabla a la izquierda para ver su contenido.")
        return

    # Validar el nombre contra la lista de tablas reales (evita inyección)
    valid_tables = safe_get_tables()
    if table_name not in valid_tables:
        st.error("Tabla no válida o no encontrada: " + str(table_name))
        return

    st.subheader(f"Vista rápida: `{table_name}`")
    # Construir consulta segura: no parametrizamos el nombre de la tabla, pero ya lo validamos.
    query = f"SELECT * FROM `{table_name}` LIMIT 100;"
    try:
        rows = run_query(query, fetch=True)
        if rows is None:
            st.info("La consulta no devolvió resultados o falló.")
            return
        if isinstance(rows, list) and len(rows) == 0:
            st.info("La tabla está vacía.")
            return
        # Mostrar dataframe
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("Error al leer tabla: " + str(e))


# ---------------- Main app layout ----------------
def main():
    st.title("📘 SGAPC - Menú principal")
    st.write("Bienvenido al sistema. Usa la barra lateral para iniciar sesión y abrir las tablas.")

    # Comprobamos la conexión (mostramos en la página de inicio)
    connected = show_connection_status()

    # Si hay conexión, intentamos listar tablas (pero la vista completa requiere login)
    tables = safe_get_tables() if connected else []

    # ---- Autenticación ----
    user = require_login_local()

    if not user:
        st.info("Debes iniciar sesión para ver las tablas y contenidos. Usa el panel lateral.")
        # opcional: no mostramos nada más hasta login
        return

    # Usuario logueado -> mostrar contenido principal y barra lateral con tablas
    st.markdown(f"**Conectado como:** `{user.get('username', user.get('display_name','usuario'))}`")

    # Sidebar: desplegable con tablas (aparece solo después de login)
    with st.sidebar:
        st.header("Navegación")
        st.text_input("Buscar page o tabla...", key="search_box")

        # Expander que contiene la lista de tablas
        with st.expander("Tablas (haz clic para seleccionar)", expanded=True):
            if not tables:
                st.write("No se detectaron tablas.")
            else:
                # Lista con botones (un solo select es más elegante)
                selected = st.radio("Selecciona una tabla", options=tables, key="selected_table_radio")
                st.write("")  # espacio
                st.caption(f"{len(tables)} tablas detectadas.")
                # Botón de cierre de sesión si existe logout_user
                if auth_available:
                    try:
                        if st.button("Cerrar sesión"):
                            try:
                                logout_user()
                            except Exception:
                                # fallback
                                st.session_state.pop("user", None)
                            st.experimental_rerun()
                    except Exception:
                        pass
                else:
                    if st.button("Cerrar sesión (modo prueba)"):
                        st.session_state.pop("user", None)
                        st.experimental_rerun()

        # Opcional: atajos o links (no los quieres, así que están minimizados)
        # st.write("---")
        # st.write("Atajos desactivados por estética.")

    # Mostrar la tabla seleccionada en el cuerpo principal
    selected_table = st.session_state.get("selected_table_radio", None)
    if selected_table:
        show_table_data(selected_table)
    else:
        st.info("Selecciona una tabla desde la barra lateral para ver su contenido.")


if __name__ == "__main__":
    main()
