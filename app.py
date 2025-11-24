import streamlit as st
from auth.login import login_user
from auth.config import check_login

st.set_page_config(
    page_title="SGAPC - Menú",
    page_icon="📘",
    layout="wide"
)

# --- AUTENTICACIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_user()
    st.stop()

check_login()

# -------------------- MENÚ PRINCIPAL --------------------
st.title("📘 SGAPC - Menú")
st.write("Usa el menú de la izquierda para navegar entre los módulos.")

with st.sidebar:
    st.header("📂 Navegación")
    st.write("Selecciona un CRUD para operar.")

    st.page_link("pages/01_acta_crudy.py", label="Acta")
    st.page_link("pages/02_administrador_crudy.py", label="Administrador")
    st.page_link("pages/03_ahorro_crudy.py", label="Ahorro")
    st.page_link("pages/04_aporte_crudy.py", label="Aporte")
    st.page_link("pages/05_asistencia_crudy.py", label="Asistencia")
    st.page_link("pages/06_caja_crudy.py", label="Caja")
    st.page_link("pages/07_ciclo_crudy.py", label="Ciclo")
    st.page_link("pages/08_cierre_crudy.py", label="Cierre")
    st.page_link("pages/09_cuota_crudy.py", label="Cuota")
    st.page_link("pages/10_directiva_crudy.py", label="Directiva")
    st.page_link("pages/11_distrito_crudy.py", label="Distrito")
    st.page_link("pages/12_grupo_crudy.py", label="Grupo")
    st.page_link("pages/13_miembro_crudy.py", label="Miembro")
    st.page_link("pages/14_multa_crudy.py", label="Multa")
    st.page_link("pages/15_pago_crudy.py", label="Pago")
    st.page_link("pages/16_prestamo_crudy.py", label="Prestamo")
    st.page_link("pages/17_promotora_crudy.py", label="Promotora")
    st.page_link("pages/18_reporte_crudy.py", label="Reporte")
    st.page_link("pages/19_reunion_crudy.py", label="Reunion")
    st.page_link("pages/20_tipo_usuario_crudy.py", label="Tipo de Usuario")
