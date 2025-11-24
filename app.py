# app.py
import streamlit as st
from db import test_connection, get_table_names
from auth.login import require_login, login_box

st.set_page_config(page_title="SGAPC", layout="wide")

def hero_login():
    """
    Pantalla de bienvenida estilo 'hero' con el formulario de login a la derecha.
    """
    st.markdown(
        """
        <style>
        .hero {
            background: linear-gradient(90deg, rgba(10,25,47,1) 0%, rgba(3,37,65,1) 100%);
            padding: 50px;
            border-radius: 8px;
        }
        .hero h1 { font-size: 48px; margin-bottom: 10px; }
        .hero p { font-size: 16px; color: #ddd; }
        </style>
        """, unsafe_allow_html=True
    )

    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown("### Bienvenido a SGAPC")
        st.markdown("Sistema para gestión de grupos. Inicia sesión para acceder.")
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[1]:
        # form in sidebar-like card area
        st.markdown("## Iniciar sesión")
        login_box(prefix="main")  # usa keys con prefijo "main"

def authenticated_ui():
    """
    Interfaz principal que aparece después de iniciar sesión.
    Sidebar con tablas y atajos.
    """
    st.sidebar.title("Navegación")
    st.sidebar.caption("Buscar page o tabla...")
    # listado de tablas detectadas
    tables = get_table_names()
    # mostrar lista desplegable (solo si hay tablas)
    if tables:
        # agrupar por columnas visuales
        with st.sidebar.expander("Ver tablas"):
            for t in tables:
                # mostramos nombre presentable (capitalizado)
                pretty = t.replace("_", " ").title()
                # link a la page correspondiente (si usas pages con ese nombre)
                # asumimos que la page se llama exactamente "01_acta_crud" etc.
                # de todas formas mostramos el link que abre la url con parámetro page
                page_link = f"?page={t}"
                st.markdown(f"- [{pretty}]({page_link})")
    else:
        st.sidebar.info("No se detectaron tablas.")

    st.title("SGAPC - Menú principal")
    st.write("Bienvenido al sistema. Usa el menú lateral (Pages) para abrir los CRUDs.")

    # Quick DB test
    ok, msg = test_connection()
    if ok:
        st.success(f"Conexión establecida ✅ — {msg}")
    else:
        st.error(f"Error de conexión a la BD: {msg}")

    st.subheader("Tablas detectadas:")
    if tables:
        st.write(", ".join(tables))
    else:
        st.write("No se detectaron tablas.")

    st.markdown("---")
    st.subheader("Accesos rápidos (Pages)")
    # intenta generar enlaces a pages si existieran con nombres similares
    if tables:
        for t in tables[:30]:
            pretty = t.replace("_", " ").title()
            st.markdown(f"- [{pretty}](?page={t})")

def main():
    st.experimental_singleton.clear()  # opcional: limpiar singletons si hiciste cambios
    # Si no hay sesión, mostrar hero + login y detener
    if not st.session_state.get("user"):
        hero_login()
        # require que el usuario inicie sesión desde la página principal:
        # no llamamos require_login aquí (porque login_box ya se mostró),
        # pero detenemos ejecución hasta que haga login en el formulario.
        st.stop()

    # Si llegamos aquí significa que el usuario está autenticado
    user = st.session_state.get("user")
    # show small user info
    st.sidebar.markdown(f"**Conectado como:** {user.get('username')}")
    authenticated_ui()

if __name__ == "__main__":
    main()
