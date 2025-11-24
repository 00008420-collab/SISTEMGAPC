# pages/08_grupo_crud.py
import streamlit as st
from db import run_query
from auth.login import require_login

require_login()
PREFIX = "grupo_"
st.set_page_config(layout="wide")
st.title("Grupos - CRUD")

rows = run_query("SELECT * FROM `grupo` ORDER BY id_grupo DESC LIMIT 300;", fetch=True)
if rows is None:
    st.error("Error listando grupos.")
else:
    st.dataframe(rows)

st.divider()
with st.form(key=PREFIX + "create"):
    st.subheader("Crear grupo")
    id_ciclo = st.text_input("id_ciclo", key=PREFIX + "id_ciclo")
    id_miembro = st.text_input("id_miembro", key=PREFIX + "id_miembro")
    id_administrador = st.text_input("id_administrador", key=PREFIX + "id_administrador")
    id_promotora = st.text_input("id_promotora", key=PREFIX + "id_promotora")
    nombre = st.text_input("nombre", key=PREFIX + "nombre")
    fecha_inicio = st.date_input("fecha_inicio", key=PREFIX + "fecha_inicio")
    fecha_interes = st.date_input("fecha_interes", key=PREFIX + "fecha_interes")
    tipo_multa = st.text_input("tipo_de_multa", key=PREFIX + "tipo_multa")
    frecuencia_reuniones = st.text_input("frecuencia_de_reuniones", key=PREFIX + "frecuencia")
    politicas_prestamo = st.text_area("politicas_de_prestamo", key=PREFIX + "politicas")
    estado = st.text_input("estado", key=PREFIX + "estado")
    submit = st.form_submit_button("Crear")
if submit:
    q = """INSERT INTO `grupo` (id_ciclo, id_miembro, id_administrador, id_promotora, nombre, fecha_inicio, fecha_interes, tipo_de_multa, frecuencia_de_reuniones, politicas_de_prestamo, estado)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    ok = run_query(q, (id_ciclo or None, id_miembro or None, id_administrador or None, id_promotora or None, nombre or None, fecha_inicio.isoformat() if hasattr(fecha_inicio,"isoformat") else fecha_inicio, fecha_interes.isoformat() if hasattr(fecha_interes,"isoformat") else fecha_interes, tipo_multa or None, frecuencia_reuniones or None, politicas_prestamo or None, estado or None), fetch=False)
    if ok:
        st.success("Grupo creado.")
        st.experimental_rerun()
    else:
        st.error("Error creando grupo.")

st.divider()
st.subheader("Editar / Eliminar grupo")
id_edit = st.text_input("id_grupo a editar/eliminar", key=PREFIX + "edit_id")
if id_edit:
    r = run_query("SELECT * FROM `grupo` WHERE id_grupo=%s LIMIT 1;", (id_edit,), fetch=True)
    if r:
        rec = r[0]
        with st.form(key=PREFIX + "edit_form"):
            # mostrar campos similares
            nombre_e = st.text_input("nombre", value=rec.get("nombre") or "", key=PREFIX + "nombre_e")
            estado_e = st.text_input("estado", value=rec.get("estado") or "", key=PREFIX + "estado_e")
            save = st.form_submit_button("Guardar cambios")
            delete = st.form_submit_button("Eliminar registro")
        if save:
            q = "UPDATE `grupo` SET nombre=%s, estado=%s WHERE id_grupo=%s;"
            ok = run_query(q, (nombre_e or None, estado_e or None, id_edit), fetch=False)
            if ok:
                st.success("Grupo actualizado.")
                st.experimental_rerun()
            else:
                st.error("Error actualizando.")
        if delete:
            ok = run_query("DELETE FROM `grupo` WHERE id_grupo=%s;", (id_edit,), fetch=False)
            if ok:
                st.success("Grupo eliminado.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar.")
    else:
        st.warning("No se encontró grupo con ese id.")
