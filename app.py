import streamlit as st

st.set_page_config(page_title="Proyecto SGI", page_icon="📋")

st.title("✔ La app ha iniciado correctamente")
st.write("Si ves este mensaje, el despliegue en Streamlit fue exitoso.")
st.write("Ahora podemos integrar tus 19 CRUDs sin errores.")

from auth import show_login_streamlit
user = show_login_streamlit()
if not user:
    st.stop()  # no continúa si no está autenticado
