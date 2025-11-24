import streamlit as st
from auth.login import login_user
from db import get_table_names, get_connection

# ------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------------------
st.set_page_config(
    page_title="SGAPC - Sistema",
    layout="wide",
)

# ------------------------------------------
# BARRA LATERAL (LOGIN)
# ------------------------------------------
login_user()

# Si no hay usuario logueado, detenemos la app
if "user" not in st.session_state:
    st.stop()

# ------------------------------------------
# INTERFAZ PRINCIPAL
# ------------------------------------------
st.markdown(
    """
    <h1 style="text-align:center; color:#004aad;">SGAPC - Sistema de Gestión</h1>
    <p style="text-align:center;">Bienvenido al sistema. Usa el menú izquierdo para acceder a los módulos.</p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ------------------------------------------
# MENÚ ELEGANTE (SIN BOTONES QUE USAN switch_page)
# SOLO DISEÑO VISUAL
# ------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style="
            background-color:#e9f2ff; 
            border-radius:12px; 
            padding:20px; 
            text-align:center;
            border:1px solid #8bb9ff;">
            <h3 style="color:#004aad;">Actas</h3>
            <p>Registra y consulta actas de reuniones del sistema.</p>
            <p style="font-size:12px; color:gray;">(Abrir desde Pages)</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style="
            background-color:#e9f2ff; 
            border-radius:12px; 
            padding:20px; 
            text-align:center;
            border:1px solid #8bb9ff;">
            <h3 style="color:#004aad;">Miembros</h3>
            <p>Gestión completa de datos de los miembros.</p>
            <p style="font-size:12px; color:gray;">(Abrir desde Pages)</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style="
            background-color:#e9f2ff; 
            border-radius:12px; 
            padding:20px; 
            text-align:center;
            border:1px solid #8bb9ff;">
            <h3 style="color:#004aad;">Préstamos</h3>
            <p>Solicitudes, aprobación y registro de préstamos.</p>
            <p style="font-size:12px; color:gray;">(Abrir desde Pages)</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ------------------------------------------
# COMPROBACIÓN DE BASE DE DATOS
# ------------------------------------------

st.subheader("🔍 Comprobación de la base de datos")

try:
    with get_connection() as conn:
        st.success("✔ Conectado a la base de datos")
        try:
            tables = get_table_names()
            st.write("Tablas encontradas:")
            st.code(", ".join(tables))
        except Exception as e:
            st.warning(f"No fue posible listar las tablas. Error: {e}")
except Exception as e:
    st.error(f"❌ No se pudo conectar a la base de datos: {e}")

st.info("Usa el menú lateral (Pages) para acceder a los módulos CRUD.")
