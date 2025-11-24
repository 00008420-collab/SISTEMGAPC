# app.py
"""
SGAPC - Menú principal (Custom)
Este archivo muestra un menú, comprueba conexión a BD y lista Pages.
Dependencias: db.py con test_connection() y get_table_names().
"""
from pathlib import Path
import os
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# Importar funciones de db (debe existir db.py)
try:
    from db import test_connection, get_table_names
except Exception:
    # Stubs si no existe db.py para que la app cargue sin fallar por import
    def test_connection():
        return False, "db.py no disponible"

    def get_table_names():
        return []

# --- Configuración de la página ---
st.set_page_config(page_title="SGAPC - Menú principal (Custom)", layout="wide", initial_sidebar_state="expanded")

# --- Helpers ---
def redirect_to_page(page_name: str):
    """Redirige el navegador a la page de Streamlit: ?page=<page_name>"""
    if not page_name:
        return
    page_enc = urllib.parse.quote(page_name, safe='')
    href = f"?page={page_enc}"
    js = f"<script>window.location.href = '{href}';</script>"
    # height=0 para no ocupar espacio
    components.html(js, height=0)

def load_pages_from_folder(pages_folder="pages"):
    """Lista los archivos .py en la carpeta pages y devuelve lista de page ids (sin .py)"""
    pages_path = Path(pages_folder)
    if not pages_path.exists() or not pages_path.is_dir():
        return []
    pages = []
    for f in sorted(os.listdir(pages_folder)):
        if f.endswith(".py") and not f.startswith("_"):
            pages.append(f[:-3])
    return pages

def pretty_name_from_page(page_id: str):
    """Convierte page id a nombre legible: '01_acta_crud' -> 'Acta'"""
    if not page_id:
        return page_id
    name = page_id
    if "_" in name:
        parts = name.split("_")
        meaningful = [p for p in parts if not p.isdigit() and p.lower() not in ("crud", "page")]
        if meaningful:
            name = " ".join(meaningful)
        else:
            name = "_".join(parts[1:])
    name = name.replace("_", " ").strip().title()
    return name

def find_best_page_for_table(table_name: str, pages_list: list):
    """Busca una page cuya id contenga el nombre de la tabla (o viceversa)."""
    if not table_name or not pages_list:
        return None
    tn = table_name.lower()
    # 1) substring match
    for p in pages_list:
        if tn in p.lower():
            return p
    # 2) part match
    for p in pages_list:
        for part in p.lower().split("_"):
            if part and part == tn:
                return p
    # 3) fallback: primera page ending _crud
    for p in pages_list:
        if p.lower().endswith("_crud"):
            return p
    return None

# --- App header / layout ---
st.title("📘 SGAPC - Menú principal (Custom)")
st.write("Bienvenido al sistema. Usa el menú lateral (o Pages) para abrir los CRUDs.")

# load available pages
pages_list = load_pages_from_folder("pages")

# Top row: two columns
col1, col2 = st.columns([3, 1])

with col1:
    st.header("🔎 Comprobación rápida de la base de datos")

    # Intentamos conexión a BD
    try:
        ok, message = test_connection()
    except Exception as e:
        ok = False
        message = f"Error al ejecutar test_connection(): {e}"

    if ok:
        st.success("Conexión establecida ✅")
    else:
        st.error(f"Error de conexión a la BD: {message}")

    # obtener tablas
    tables = []
    try:
        tables = get_table_names() or []
    except Exception as e:
        st.warning(f"No fue posible listar tablas (get_table_names error): {e}")
        tables = []

    if tables:
        st.markdown("**Tablas detectadas:**")
        st.write(", ".join(tables))
    else:
        st.info("No se detectaron tablas o hubo un error al listarlas.")

with col2:
    st.header("Atajos")
    st.write("Accesos rápidos a Pages (haz clic para abrir).")
    if pages_list:
        for p in pages_list:
            pretty = pretty_name_from_page(p)
            st.markdown(f"- [{p}](?page={urllib.parse.quote(p)})  \n  `({pretty})`")
    else:
        st.info("No hay Pages detectadas en la carpeta /pages.")

st.markdown("---")

# --- Quick buttons grid (cards) ---
st.subheader("Atajos visuales")
if pages_list:
    cols = st.columns(3)
    for i, p in enumerate(pages_list):
        c = cols[i % 3]
        pretty = pretty_name_from_page(p)
        with c:
            st.markdown(f"#### {pretty}")
            st.caption(f"Page id: `{p}`")
            if st.button(f"Abrir {pretty}", key=f"open_{p}"):
                redirect_to_page(p)
else:
    st.info("No hay Pages (archivos en /pages) para mostrar atajos visuales.")

st.markdown("---")

# --- Sidebar: lista buscable de pages ---
with st.sidebar:
    st.title("Navegación")
    q = st.text_input("Buscar", value="", placeholder="Buscar page o tabla...")
    st.write("Pages:")
    filtered = [p for p in pages_list if q.lower() in p.lower() or q.lower() in pretty_name_from_page(p).lower()]
    for p in filtered:
        label = pretty_name_from_page(p)
        if st.button(label, key=f"sb_{p}"):
            redirect_to_page(p)

    st.markdown("---")
    st.write("Opción rápida: selecciona la Page exacta desde el menú lateral 'Pages'.")

# --- Extra: buscar tabla y abrir su page correspondiente ---
st.subheader("Abrir CRUD por tabla")
if tables:
    table_sel = st.selectbox("Selecciona una tabla", options=["-- elegir --"] + tables)
    if table_sel and table_sel != "-- elegir --":
        page_candidate = find_best_page_for_table(table_sel, pages_list)
        st.write(f"Page sugerida: `{page_candidate}`" if page_candidate else "No se encontró Page sugerida.")
        cola, colb = st.columns([1, 1])
        with cola:
            if st.button("Abrir Page sugerida"):
                if page_candidate:
                    redirect_to_page(page_candidate)
                else:
                    st.info("No hay Page sugerida, abre manualmente desde Pages.")
        with colb:
            if st.button("Buscar Pages que contengan tabla"):
                matches = [p for p in pages_list if table_sel.lower() in p.lower()]
                if matches:
                    st.write("Matches:")
                    for m in matches:
                        st.write(f"- `{m}`")
                        if st.button(f"Ir a {m}", key=f"goto_{m}"):
                            redirect_to_page(m)
                else:
                    st.info("No se encontraron Pages que contengan el nombre de la tabla.")
else:
    st.info("No hay tablas disponibles para buscar.")

# --- Footer / debug info ---
st.markdown("---")
st.caption(f"Generado: {datetime.utcnow().isoformat()} UTC")
st.caption("Si los atajos no funcionan, revisa la versión de Streamlit (algunas versiones no actualizan el menú Pages automáticamente).")
