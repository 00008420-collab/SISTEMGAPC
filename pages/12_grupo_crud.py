import streamlit as st
from crud_template import render_crud
table="grupo"
pk="id_grupo"
cols=["id_grupo","id_ciclo","id_miembro","id_administrador","id_promotora","nombre","fecha_inicio","fecha_interes","tipo_de_multa","frecuencia_de_reuniones","politicas_de_prestamo","estado"]
render_crud(table, pk, cols)
