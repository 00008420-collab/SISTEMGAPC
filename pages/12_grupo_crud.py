# pages/12_grupo_crud.py
import streamlit as st
from db import get_connection
from datetime import date

TABLE = "grupo"
ID_COL = "id_grupo"

st.title("Grupo — CRUD")

def list_grupos(limit=200):
    conn = get_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE}` LIMIT %s",(limit,))
            return cur.fetchall()
    finally:
        conn.close()

def create_grupo(id_ciclo, id_miembro, id_administrador, id_promotora, nombre, fecha_inicio, fecha_interes, tipo_multa, frecuencia_reuniones, politicas_prestamo, estado):
    conn = get_connection()
    if not conn: return False,"no conn"
    try:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE}` (`id_ciclo`,`id_miembro`,`id_administrador`,`id_promotora`,`nombre`,`fecha_inicio`,`fecha_interes`,`tipo_de_multa`,`frecuencia_de_reuniones`,`politicas_de_prestamo`,`estado`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio,fecha_interes,tipo_multa,frecuencia_reuniones,politicas_prestamo,estado))
            conn.commit()
            return True,"Creado"
    except Exception as e:
        return False,str(e)
    finally:
        conn.close()

with st.expander("Listar grupos"):
    limit = st.number_input("Límite",value=200,min_value=10)
    if st.button("Cargar grupos"):
        st.dataframe(list_grupos(limit))

st.markdown("---")
st.subheader("Crear grupo")
with st.form("create_grupo"):
    id_ciclo = st.text_input("id_ciclo")
    id_miembro = st.text_input("id_miembro")
    id_administrador = st.text_input("id_administrador")
    id_promotora = st.text_input("id_promotora")
    nombre = st.text_input("nombre")
    fecha_inicio = st.date_input("fecha_inicio")
    fecha_interes = st.date_input("fecha_interes")
    tipo_multa = st.text_input("tipo_de_multa")
    frecuencia_reuniones = st.text_input("frecuencia_de_reuniones")
    politicas_prestamo = st.text_area("politicas_de_prestamo")
    estado = st.text_input("estado")
    if st.form_submit_button("Crear"):
        ok,msg = create_grupo(id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio.isoformat(),fecha_interes.isoformat(),tipo_multa,frecuencia_reuniones,politicas_prestamo,estado)
        if ok: st.success(msg)
        else: st.error(msg)

st.markdown("---")
st.subheader("Buscar / Editar / Eliminar por id_grupo")
buscar = st.text_input("id_grupo")
if st.button("Cargar"):
    if not buscar: st.warning("Ingresa id")
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                rec = cur.fetchone()
            if not rec: st.info("No encontrado")
            else:
                st.json(rec)
                with st.form("update_grupo"):
                    id_ciclo = st.text_input("id_ciclo", value=str(rec.get("id_ciclo") or ""))
                    id_miembro = st.text_input("id_miembro", value=str(rec.get("id_miembro") or ""))
                    id_administrador = st.text_input("id_administrador", value=str(rec.get("id_administrador") or ""))
                    id_promotora = st.text_input("id_promotora", value=str(rec.get("id_promotora") or ""))
                    nombre = st.text_input("nombre", value=str(rec.get("nombre") or ""))
                    try:
                        fi = date.fromisoformat(str(rec.get("fecha_inicio")))
                        fe = date.fromisoformat(str(rec.get("fecha_interes")))
                    except Exception:
                        fi = date.today(); fe = date.today()
                    fecha_inicio = st.date_input("fecha_inicio", value=fi)
                    fecha_interes = st.date_input("fecha_interes", value=fe)
                    tipo_multa = st.text_input("tipo_de_multa", value=str(rec.get("tipo_de_multa") or ""))
                    frecuencia_reuniones = st.text_input("frecuencia_de_reuniones", value=str(rec.get("frecuencia_de_reuniones") or ""))
                    politicas_prestamo = st.text_area("politicas_de_prestamo", value=str(rec.get("politicas_de_prestamo") or ""))
                    estado = st.text_input("estado", value=str(rec.get("estado") or ""))
                    if st.form_submit_button("Actualizar"):
                        try:
                            with get_connection().cursor() as cur2:
                                cur2.execute(f"UPDATE `{TABLE}` SET `id_ciclo`=%s,`id_miembro`=%s,`id_administrador`=%s,`id_promotora`=%s,`nombre`=%s,`fecha_inicio`=%s,`fecha_interes`=%s,`tipo_de_multa`=%s,`frecuencia_de_reuniones`=%s,`politicas_de_prestamo`=%s,`estado`=%s WHERE `{ID_COL}`=%s",
                                             (id_ciclo,id_miembro,id_administrador,id_promotora,nombre,fecha_inicio.isoformat(),fecha_interes.isoformat(),tipo_multa,frecuencia_reuniones,politicas_prestamo,estado,buscar))
                                get_connection().commit()
                            st.success("Actualizado")
                        except Exception as e:
                            st.error(f"Error: {e}")
                if st.button("Eliminar"):
                    try:
                        with get_connection().cursor() as cur3:
                            cur3.execute(f"DELETE FROM `{TABLE}` WHERE `{ID_COL}`=%s",(buscar,))
                            get_connection().commit()
                        st.success("Eliminado")
                    except Exception as e:
                        st.error(f"Error: {e}")
