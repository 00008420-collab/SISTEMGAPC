# app.py
import os
import streamlit as st
from auth.login import require_login
from db import get_table_names, run_query

st.set_page_config(page_title="SGAPC - Menú", layout="wide")

# -----------------------------
# Helpers (estética y util)
# -----------------------------
def pretty_name(table_name: str) -> str:
    """Convierte 'tipo_usuario' -> 'Tipo Usuario'"""
    return table_name.replace("_", " ").strip().title()

def discover_pages():
    """
    Lee la carpeta 'pages' y devuelve los nombres de page (sin .py).
    Esto ayuda a mapear tablas -> page exacto que el menú de Streamlit muestra.
    """
    pages_dir = "pages"
    if not os.path.isdir(pages_dir):
        return []
    files = []
    for f in os.listdir(pages_dir):
        if f.endswith(".py") and not f.startswith("__"):
            files.append(f[:-3])  # quitar .py
    # Orden alfabético para consistencia
    return sorted(files)

def find_best_page_for_table(table_name: str, pages_list):
    """
    Intenta encontrar el nombre exacto de Page para la tabla:
    - Busca coincidencia exacta
    - Busca page que contenga la tabla (p. ej. '01_acta_crud' contiene 'acta')
    - Si no encuentra, devuelve None
    """
    # coincidencia exacta
    if table_name in pages_list:
        return table_name
    # buscar por subcadena
    candidates = [p for p in pages_list if table_name in p]
    if candidates:
        return candidates[0]
    # buscar por pretty name
    pretty = pretty_name(table_name).lower().replace(" ", "_")
    for p in pages_list:
        if pretty in p:
            return p
    return None

# -----------------------------
# Sidebar personalizado
# -----------------------------
def sidebar_tables_panel():
    user = require_login()
    if not user:
        return None

    # Cabecera sidebar
    st.sidebar.markdown(f"### 📘 SGAPC — {user.get('full_name') or user.get('username')}")
    st.sidebar.caption(f"Conectado como: **{user.get('username')}** — {user.get('role', '')}")

    # Buscador
    search = st.sidebar.text_input("🔎 Buscar tabla...", value="", key="sidebar_table_search")

    # Detectar tablas y páginas
    tables = get_table_names() or []
    pages_list = discover_pages()

    with st.sidebar.expander("📂 Tablas", expanded=True):
        if not tables:
            st.write("No se detectaron tablas.")
        else:
            # Filtrar y ordenar
            filtered = sorted([t for t in tables if search.lower() in t.lower()]) if search else sorted(tables)
            # Mostrar selectbox elegante (más compacto)
            pretty_choices = [pretty_name(t) for t in filtered]
            if pretty_choices:
                choice_idx = st.selectbox("Selecciona una tabla", options=list(range(len(pretty_choices))),
                                          format_func=lambda i: pretty_choices[i], key="sidebar_table_select")
                if st.button("Abrir Page", key="sidebar_open_btn"):
                    chosen_table = filtered[choice_idx]
                    page_target = find_best_page_for_table(chosen_table, pages_list)
                    if page_target:
                        try:
                            st.experimental_set_query_params(page=page_target)
                            st.success(f"Intentando abrir la Page: **{page_target}**")
                        except Exception:
                            st.info(f"Abre la Page manualmente desde el menú 'Pages' y selecciona: **{page_target}**")
                    else:
                        st.info(f"No se encontró una Page automática para **{chosen_table}**. Abre la Page correspondiente manualmente.")

            # También mostrar botones individuales (opcional, útil para listas largas)
            st.write("---")
            st.write("O abrir rápidamente:")
            for t in filtered:
                label = pretty_name(t)
                if st.button(label, key=f"btn_{t}"):
                    page_target = find_best_page_for_table(t, pages_list)
                    if page_target:
                        try:
                            st.experimental_set_query_params(page=page_target)
                            st.success(f"Intentando abrir la Page: **{page_target}**")
                        except Exception:
                            st.info(f"Abre la Page manualmente desde el menú 'Pages' y selecciona: **{page_target}**")
                    else:
                        st.info(f"No se encontró Page para **{label}**. Abre la Page manualmente desde 'Pages'.")

    st.sidebar.markdown("---")
    if st.sidebar.button("🔒 Cerrar sesión"):
        try:
            from auth.helpers import clear_current_user
            clear_current_user()
            st.experimental_rerun()
        except Exception:
            st.sidebar.info("Sesión cerrada (si existe). Refresca la página.")
    return user

# Ejecutar sidebar
current_user = sidebar_tables_panel()

# -----------------------------
# Area principal
# -----------------------------
def main_area(user):
    st.title("SGAPC - Menú principal (Custom)")
    st.markdown("Bienvenido al sistema. Usa el menú lateral (o Pages) para abrir los CRUDs.")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("Comprobación rápida de la base de datos")
        try:
            # prueba simple de conexión / consulta
            rows = run_query("SELECT 1 as ok;", fetch=True)
            if rows:
                st.success("Conexión establecida ✅")
            else:
                st.error("Conexión establecida, pero la consulta mostró resultado inesperado.")
        except Exception as e:
            st.error(f"Error de conexión a la BD: {e}")

        # Mostrar tablas detectadas
        tables = get_table_names() or []
        if tables:
            st.write("Tablas detectadas:")
            st.write(", ".join(tables))
        else:
            st.info("No se detectaron tablas o no es posible listarlas.")

    with col2:
        st.header("Atajos")
        st.write("Accesos rápidos a Pages (si tu versión de Streamlit lo permite, se abrirán automáticamente).")
        pages_list = discover_pages()
        for p in pages_list[:12]:
            st.write(f"- `{p}`")

    st.markdown("---")
    st.info("Si la navegación automática no te lleva a la Page correcta, abre la Page manualmente desde el menú lateral 'Pages'.")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    user = current_user
    main_area(user)
