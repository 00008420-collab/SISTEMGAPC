# app.py
import streamlit as st
from pathlib import Path

# intenta importar get_connection si existe (tu db.py)
try:
    from db import get_connection, get_table_names
except Exception:
    get_connection = None
    get_table_names = None

st.set_page_config(page_title="SGAPC - Menú", layout="wide")

# ---------- helpers ----------
def try_switch(page_name):
    """Intenta cambiar a la page indicada. Si switch_page no existe, muestra instrucción."""
    try:
        st.experimental_set_query_params()  # for safety/reset
        st.switch_page(page_name)
    except Exception as e:
        # si switch_page no está disponible, explicamos cómo abrir la page desde el menú Pages
        st.warning(
            "Navegación automática no disponible (versión de Streamlit). "
            "Abre la página desde el menú lateral 'Pages' o actualiza Streamlit."
        )
        st.info(f"Nombre de page objetivo: **{page_name}**")
        st.write("También puedes usar el menú izquierdo (Pages) para abrir directamente el CRUD.")

def make_btn(col, label, page_name, key=None):
    """Crea un botón en la columna y realiza switch a page_name al pulsarlo."""
    if col.button(label, key=key or label):
        try_switch(page_name)

# ---------- lista de pages / mapping ----------
# Ajusta aquí los nombres exactos de tus archivos en /pages (sin .py)
# Usa los nombres que realmente tienes en la carpeta pages/
PAGES = [
    ("01_acta_crud", "Acta"),
    ("02_administrador_crud", "Administrador"),
    ("03_ahorro_crud", "Ahorro"),
    ("04_aporte_crud", "Aporte"),
    ("05_asistencia_crud", "Asistencia"),
    ("06_caja_crud", "Caja"),
    ("07_ciclo_crud", "Ciclo"),
    ("08_cierre_crud", "Cierre"),
    ("09_cuota_crud", "Cuota"),
    ("10_directiva_crud", "Directiva"),
    ("11_distrito_crud", "Distrito"),
    ("12_grupo_crud", "Grupo"),
    ("13_miembro_crud", "Miembro"),
    ("14_multa_crud", "Multa"),
    ("15_pago_crud", "Pago"),
    ("16_prestamo_crud", "Prestamo"),
    ("17_promotora_crud", "Promotora"),
    ("18_reporte_crud", "Reporte"),
    ("19_reunion_crud", "Reunion"),
    ("20_tipo_usuario_crud", "Tipo_usuario"),
    # si tienes users u otro archivo, agréga aquí
    ("users_crud", "Users (opcional)"),
]

# ---------- UI ----------
st.title("📘 SGAPC - Menú principal (Custom)")
st.write("Usa los botones abajo para abrir los CRUDs. Si la navegación automática no funciona, abre las Pages desde el menú izquierdo.")

# fila superior: comprobación de conexión (opcional)
with st.expander("🔍 Comprobación rápida de BD", expanded=True):
    if get_connection:
        try:
            conn = get_connection()
            if conn:
                st.success("Conexión establecida ✅")
                try:
                    tables = get_table_names(conn)
                    if tables:
                        st.write("Se detectaron tablas:", ", ".join(tables))
                except Exception:
                    st.info("No fue posible listar tablas (get_table_names no disponible o error).")
            else:
                st.error("No se pudo obtener conexión (get_connection retornó None).")
        except Exception as e:
            st.error("Error conectando a la BD: " + str(e))
    else:
        st.info("No se encontró la función get_connection. Si quieres comprobar BD aquí, añade get_connection en db.py")

st.markdown("---")

# Grid de botones: 3 columnas
cols = st.columns(3)
for i, (page_file, label) in enumerate(PAGES):
    col = cols[i % 3]
    make_btn(col, label, page_file, key=f"btn_{i}")

st.markdown("---")

# enlace al PDF del proyecto (ruta local subida)
pdf_path = Path("/mnt/data/Proyecto final rev.pdf")
if pdf_path.exists():
    st.markdown("### 📎 Documentos")
    # mostramos un botón que abre el pdf en una nueva pestaña (si el hosting lo permite)
    st.markdown(f"[Abrir proyecto (PDF)]({pdf_path})")
else:
    st.info("PDF del proyecto no encontrado en /mnt/data/Proyecto final rev.pdf")

st.caption("Si al pulsar un botón no ocurre nada: 1) asegúrate de que el archivo .py correspondiente exista en /pages, 2) revisa logs en Streamlit Cloud y 3) si la app usa una versión vieja de Streamlit, la navegación automática `st.switch_page` puede no estar disponible.")
