# app.py - Menú elegante para SGAPC
import streamlit as st
from pathlib import Path
from textwrap import shorten

# intenta importar helpers de db
try:
    from db import get_connection, get_table_names
except Exception:
    get_connection = None
    get_table_names = None

st.set_page_config(page_title="SGAPC - Menú", layout="wide", initial_sidebar_state="expanded")

# -------------------------
# Estilos (pequeño CSS para "cards")
# -------------------------
st.markdown(
    """
    <style>
    .card {
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 18px;
        margin: 8px 6px;
        background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.00));
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        transition: transform .12s ease-in-out, box-shadow .12s ease-in-out;
    }
    .card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.45); }
    .card-title { font-size:18px; font-weight:600; margin-bottom:6px; }
    .card-desc { color: rgba(255,255,255,0.65); font-size:13px; margin-bottom:8px; }
    .card-cta { margin-top:6px; }
    .grid { display:flex; gap:12px; flex-wrap:wrap; }
    .icon { font-size:22px; margin-right:8px; vertical-align:middle; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Contenido principal
# -------------------------
st.title("📘 SGAPC — Menú principal")
st.write("Bienvenida/o — usa las tarjetas para abrir los módulos. Si la navegación automática no funciona, abre la Page correspondiente desde el menú lateral `Pages`.")

# sidebar - estado y acciones
with st.sidebar:
    st.header("🔧 Estado")
    # comprobar conexión
    if get_connection:
        try:
            conn = get_connection()
            if conn:
                st.success("Conexión establecida ✅")
            else:
                st.error("No se pudo establecer conexión.")
        except Exception as e:
            st.error("Error al conectar: " + str(e))
    else:
        st.info("get_connection() no disponible. Comprueba db.py")

    st.markdown("---")
    st.subheader("📁 Documentos")
    pdf_path = Path("/mnt/data/Proyecto final rev.pdf")
    if pdf_path.exists():
        # mostramos ruta para que Streamlit Cloud la convierta a url
        st.markdown(f"- [Ver Proyecto (PDF)]({pdf_path})")
    else:
        st.info("PDF no encontrado en /mnt/data")

    st.markdown("---")
    st.caption("¿Problemas? Ve a Manage app → Logs y pega la traza aquí.")
    st.markdown("")

# -------------------------
# Mapping de módulos (archivo_page, etiqueta, emoji, descripción corta)
# -------------------------
MODULES = [
    ("01_acta_crud", "Acta", "📝", "Registro de actas y detalles de reuniones"),
    ("02_administrador_crud", "Administrador", "👤", "Gestión de administradores y datos personales"),
    ("03_ahorro_crud", "Ahorro", "💰", "Control de ahorros y saldo por miembro"),
    ("04_aporte_crud", "Aporte", "🤲", "Aportes por reunión"),
    ("05_asistencia_crud", "Asistencia", "📋", "Registro de asistencias y justificaciones"),
    ("06_caja_crud", "Caja", "🏦", "Movimientos de caja, ingresos y egresos"),
    ("07_ciclo_crud", "Ciclo", "🔁", "Control de ciclos y periodos"),
    ("08_cierre_crud", "Cierre", "🔒", "Procesos de cierre y reportes finales"),
    ("09_cuota_crud", "Cuota", "📆", "Administración de cuotas y vencimientos"),
    ("10_directiva_crud", "Directiva", "🧭", "Integrantes de la directiva por grupo"),
    ("11_distrito_crud", "Distrito", "📍", "Zonas y distritos del proyecto"),
    ("12_grupo_crud", "Grupo", "🏘️", "Gestión de grupos y políticas"),
    ("13_miembro_crud", "Miembro", "🧑‍🤝‍🧑", "Datos de miembros y su identificación"),
    ("14_multa_crud", "Multa", "⚠️", "Multas aplicadas y estado"),
    ("15_pago_crud", "Pago", "💳", "Pagos realizados y conciliación"),
    ("16_prestamo_crud", "Prestamo", "📈", "Control de préstamos y saldos"),
    ("17_promotora_crud", "Promotora", "🚚", "Promotoras y contactos"),
    ("18_reporte_crud", "Reporte", "📊", "Generación de reportes y estadísticas"),
    ("19_reunion_crud", "Reunion", "📅", "Reuniones programadas y actas"),
    ("20_tipo_usuario_crud", "Tipo_usuario", "🔐", "Definición de roles y tipos de usuario"),
    ("users_crud", "Users (opcional)", "🔑", "Usuarios de acceso (si aplica)")
]

# grid responsiva: 3 columnas
cols = st.columns(3)
col_idx = 0

for page_file, label, emoji, desc in MODULES:
    col = cols[col_idx % 3]
    # tarjeta HTML simple
    with col:
        st.markdown(
            f"""
            <div class="card">
              <div class="card-title"><span class="icon">{emoji}</span>{label}</div>
              <div class="card-desc">{desc}</div>
            """,
            unsafe_allow_html=True,
        )

        # botón visual dentro de la card
        # al pulsar intentamos switch_page; si no funciona, mostramos instrucciones
        if st.button(f"Abrir {label}", key=f"open_{page_file}"):
            # intento de navegación automática
            try:
                st.switch_page(page_file)
            except Exception:
                st.warning("Navegación automática no disponible en esta versión de Streamlit.")
                st.info("Abre la Page desde el menú lateral (Pages).")
                st.write("Nombre exacto de la Page:")
                st.code(page_file)

        st.markdown("</div>", unsafe_allow_html=True)

    col_idx += 1

st.markdown("---")
st.caption("Consejo: si la navegación automática no funciona, abre el módulo desde el menú lateral 'Pages' (en el panel izquierdo).")

# footer con resumen de tablas (si se puede listar)
try:
    if get_table_names:
        tables = get_table_names()
        if tables:
            st.write("**Tablas detectadas:**", ", ".join(tables))
except Exception:
    pass
