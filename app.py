# app.py
"""
Página principal (landing + menú) para SGAPC.
Requisitos:
 - auth/login.py debe exponer `require_login()` (o `login_box()`).
 - db.py idealmente expone `test_connection()` y `get_table_names()`, pero
   este script maneja la ausencia de esas funciones.
Cómo funciona:
 - Abre la app -> si no hay sesión muestra la pantalla de inicio/login.
 - Tras iniciar sesión, muestra el dashboard de bienvenida y la barra lateral
   con las tablas (y opciones para intentar abrir Pages automáticamente).
"""

from typing import List, Optional, Tuple
import streamlit as st
import os
import html

# Import auth helper (require_login must stop la ejecución si no hay sesión)
try:
    from auth.login import require_login, login_box
except Exception:
    # Fallback: si falta el módulo, definimos un require_login dummy para evitar crashes.
    def login_box():
        st.warning("Falta auth/login.py. Añádelo al proyecto.")
    def require_login():
        login_box()
        st.stop()

# Import DB helpers (opcionales)
try:
    from db import test_connection, get_table_names
except Exception:
    test_connection = None
    get_table_names = None


# ---------------------------
# Helpers UI y navegación
# ---------------------------
ICON = "📘"

# Mapeo estético: nombre de página (archivo pages) -> título legible + icon
DEFAULT_PAGE_MAP = {
    "01_acta_crud": ("Actas", "📝"),
    "02_administrador_crud": ("Administradores", "👤"),
    "03_ahorro_crud": ("Ahorros", "💰"),
    "04_aporte_crud": ("Aportes", "🏦"),
    "05_asistencia_crud": ("Asistencias", "📋"),
    "06_caja_crud": ("Caja", "📥"),
    "07_ciclo_crud": ("Ciclos", "🔁"),
    "08_cierre_crud": ("Cierres", "🔒"),
    "09_cuota_crud": ("Cuotas", "📅"),
    "10_directiva_crud": ("Directiva", "🏛️"),
    "11_distrito_crud": ("Distritos", "📍"),
    "12_grupo_crud": ("Grupos", "🧑‍🤝‍🧑"),
    "13_miembro_crud": ("Miembros", "👥"),
    "14_multa_crud": ("Multas", "⚠️"),
    "15_pago_crud": ("Pagos", "💳"),
    "16_prestamo_crud": ("Préstamos", "🏦"),
    "17_promotora_crud": ("Promotoras", "📣"),
    "18_reporte_crud": ("Reportes", "📊"),
    "19_reunion_crud": ("Reuniones", "🗓️"),
    "20_tipo_usuario_crud": ("Tipos de usuario", "🔐"),
    # Add more if you have extra pages (users, permission, ...)
}

def set_query_page(page_key: str):
    """
    Intenta abrir la Page usando query params.
    Streamlit Pages puede abrirse con ?page=pagename en ciertas versiones.
    """
    try:
        # Guardar un valor en query params (intento de navegación)
        st.experimental_set_query_params(page=page_key)
    except Exception:
        # No fatal — fallback en UI
        pass


def pretty_list_from_table_names(tables: List[str]) -> List[Tuple[str, str]]:
    """
    Recibe una lista de nombres de tablas (o páginas) y devuelve pares (page_key, title)
    donde page_key será el nombre de la Page (sin sufijos).
    """
    out = []
    for t in tables:
        key = t.strip()
        # Si ya coincide con un key del DEFAULT_PAGE_MAP lo usamos,
        # si no, intentamos normalizar: quitar sufijos como "_crud" o "crud"
        norm = key
        if norm.endswith("_crud"):
            norm = norm[:-5]
        if norm.endswith("crud"):
            norm = norm[:-4]

        # buscar un key en DEFAULT_PAGE_MAP que contenga norm
        found = None
        for page_key in DEFAULT_PAGE_MAP.keys():
            if norm in page_key:
                found = page_key
                break

        if found is None:
            # Si la tabla es exactamente el nombre de una page candidate, usarla
            if key in DEFAULT_PAGE_MAP:
                found = key
        if found is None:
            # Si no se encontró, generamos un page-like key usando nombre original (limpio)
            # e.g. "mi_tabla" -> "mi_tabla_crud"
            cand = f"{norm}_crud"
            found = cand

        # Título: si está en DEFAULT_PAGE_MAP lo tomamos, si no lo capitalizamos
        title = DEFAULT_PAGE_MAP.get(found, (found.replace("_", " ").title(), "📁"))[0]
        out.append((found, title))
    return out


# ---------------------------
# Layout: hero / login screen
# ---------------------------
def show_hero_login():
    """
    Pantalla de inicio estilo 'hero' con login al centro-derecha.
    Si ya se inició sesión, esta función no hará nada.
    """
    # Si ya hay sesión, no mostrar hero
    if "logged_in" in st.session_state and st.session_state.logged_in:
        return

    st.set_page_config(page_title="SGAPC - Inicio", layout="wide")
    # Hero layout: dos columnas, izquierda visual grande, derecha formulario
    col_left, col_right = st.columns([1.4, 1])
    with col_left:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg,#0f1724,#0b1223); padding:32px; border-radius:12px;">
            <h1 style="color: #ffffff; font-size:44px; margin-bottom:6px;">Welcome Back</h1>
            <p style="color: #cbd5e1; font-size:16px; max-width:680px;">
              Bienvenido(a) al sistema de gestión. Inicia sesión para acceder a los módulos:
              miembros, aportes, préstamos, caja y más.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        # Mostrar la caja de login provista por auth/login.py
        login_box()

    # Añadimos un separador y seguimos con el resto de la página (si no logueado, require_login detendrá)
    st.markdown("---")


# ---------------------------
# Dashboard después de login
# ---------------------------
def show_dashboard(tables: List[Tuple[str, str]]):
    """
    Muestra el dashboard principal con tarjetas y shortcuts.
    tables: lista de (page_key, title)
    """
    st.title("SGAPC - Menú principal")
    st.markdown("Bienvenido al sistema. Usa la barra lateral para navegar entre módulos.")

    # Quick DB status
    db_ok = False
    db_msg = "Sin comprobación"
    if callable(test_connection):
        try:
            ok, msg = test_connection()
            db_ok = ok
            db_msg = msg
        except Exception as e:
            db_ok = False
            db_msg = f"Error comprobando DB: {e}"

    if db_ok:
        st.success(f"Conexión establecida ✅ — {db_msg}")
    else:
        st.warning(f"Conexión DB: {db_msg}")

    # Tarjetas principales (3 columnas)
    ncols = 3
    cols = st.columns(ncols)
    # Mostrar primeras 9 como tarjetas
    for idx, (page_key, title) in enumerate(tables[:9]):
        col = cols[idx % ncols]
        icon = DEFAULT_PAGE_MAP.get(page_key, ("", "📁"))[1]
        with col:
            st.markdown(
                f"""
                <div style="background:#0b1220; padding:18px; border-radius:12px; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
                  <div style="font-size:20px; font-weight:700; color:#e6edf3;">{icon} {title}</div>
                  <div style="color:#9aa7b2; margin-top:8px; font-size:13px;">
                    Abrir módulo y gestionar registros.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Abrir {title}", key=f"open_{page_key}"):
                # Intentamos navegar a la Page
                set_query_page(page_key)
                st.info(
                    f"Intentando abrir la Page `{page_key}`. "
                    "Si tu versión de Streamlit no soporta navegación automática, abre la Page desde el menú lateral (Pages)."
                )

    st.markdown("---")
    st.header("Todos los módulos")
    # Lista completa en 2 columnas:
    left, right = st.columns([1, 1])
    half = (len(tables) + 1) // 2
    for (page_key, title) in tables[:half]:
        with left:
            st.markdown(f"- [{html.escape(title)}](#)  <small style='color:#7f8a93'>`{page_key}`</small>", unsafe_allow_html=True)
            if st.button(f"Abrir {title}", key=f"open2_{page_key}"):
                set_query_page(page_key)
    for (page_key, title) in tables[half:]:
        with right:
            st.markdown(f"- [{html.escape(title)}](#)  <small style='color:#7f8a93'>`{page_key}`</small>", unsafe_allow_html=True)
            if st.button(f"Abrir {title}", key=f"open2b_{page_key}"):
                set_query_page(page_key)


# ---------------------------
# Sidebar (solo después de login)
# ---------------------------
def sidebar_menu(tables: List[Tuple[str, str]]):
    """
    Barra lateral con búsqueda y lista desplegable de páginas.
    """
    st.sidebar.title("Navegación")
    st.sidebar.markdown("Buscar módulo y navegar")

    # search input to filter tables
    q = st.sidebar.text_input("Buscar", placeholder="Buscar page o tabla...", key="search_pages")
    filtered = []
    for key, title in tables:
        if not q or q.strip().lower() in title.lower() or q.strip().lower() in key.lower():
            filtered.append((key, title))

    # Show collapsible list
    with st.sidebar.expander("Ver módulos", expanded=True):
        for key, title in filtered:
            icon = DEFAULT_PAGE_MAP.get(key, ("", "📁"))[1]
            # each module as a button
            btn_label = f"{icon}  {title}"
            if st.sidebar.button(btn_label, key=f"sb_{key}"):
                set_query_page(key)

    st.sidebar.markdown("---")
    st.sidebar.markdown("Usa el menú para abrir módulos. Si la navegación automática no funciona, abre las Pages desde el menú lateral 'Pages'.")


# ---------------------------
# Main
# ---------------------------
def main():
    st.set_page_config(page_title="SGAPC", layout="wide")

    # Mostrar hero/login si no autenticado
    show_hero_login()

    # Requerir login para continuar (esto detendrá la ejecución si no hay sesión)
    user = require_login()  # retorna user_row

    # Ya autenticado: construimos lista de tablas/páginas
    page_candidates = []
    if callable(get_table_names):
        try:
            # get_table_names puede devolver lista de tablas desde la BD
            tbls = get_table_names()
            # asegurar lista única y ordenada
            tbls = list(dict.fromkeys(tbls))
            # convertimos a (page_key, title)
            page_candidates = pretty_list_from_table_names(tbls)
        except Exception:
            page_candidates = []
    if not page_candidates:
        # fallback: usar DEFAULT_PAGE_MAP
        page_candidates = [(k, v[0]) for k, v in DEFAULT_PAGE_MAP.items()]

    # Sidebar
    sidebar_menu(page_candidates)

    # Dashboard / menú principal
    show_dashboard(page_candidates)

    # Información del usuario logueado (pequeño footer)
    st.markdown("---")
    st.write(f"Conectado como: **{user.get('username','-')}** — rol: **{user.get('role','-')}**")


if __name__ == "__main__":
    main()
