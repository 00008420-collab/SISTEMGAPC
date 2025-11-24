# pages/13_miembro_crud.py
import streamlit as st
from db import run_query
from auth import user_has_permission

def app():
    st.header("Miembro — CRUD")
    user = st.session_state.get("user")

    # Crear miembro (solo si tiene permiso 'alta_usuario' o si es administrador)
    if user and user_has_permission(user, "alta_usuario"):
        with st.expander("Crear nuevo miembro"):
            id_tipo = st.number_input("id_tipo_usuario", value=1, step=1)
            apellido = st.text_input("apellido")
            dui = st.text_input("dui")
            direccion = st.text_input("direccion")
            if st.button("Crear miembro"):
                sql = "INSERT INTO miembro (id_tipo_usuario, apellido, dui, direccion) VALUES (%s, %s, %s, %s)"
                run_query(sql, params=(id_tipo, apellido, dui, direccion))
                st.success("Miembro creado.")
    else:
        st.info("No tienes permiso para crear miembros.")

    # Solicitar préstamo (miembro)
    if user and user_has_permission(user, "solicitar_prestamo"):
        with st.form("solicitar_prestamo"):
            monto = st.number_input("Monto solicitado", min_value=1.0)
            plazo = st.number_input("Plazo (meses)", value=1, step=1)
            if st.form_submit_button("Enviar solicitud"):
                # insertar en tabla solicitud
                payload = {
                    "monto": monto,
                    "plazo": plazo
                }
                run_query(
                    "INSERT INTO solicitud (tipo, origen, id_origen, payload) VALUES (%s, %s, %s, %s)",
                    params=("prestamo", "miembro", None, str(payload))
                )
                st.success("Solicitud de préstamo enviada.")
    else:
        st.info("No tienes permiso para solicitar préstamos.")

    # Listar miembros (ejemplo)
    if st.button("Listar miembros"):
        rows = run_query("SELECT * FROM miembro LIMIT 200", fetch=True)
        if rows:
            st.dataframe(rows)
        else:
            st.info("No hay resultos o la consulta falló.")

# Permitir ejecución como script (debug)
if __name__ == "__main__":
    app()
