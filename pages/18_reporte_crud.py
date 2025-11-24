import streamlit as st
from crud_template import render_crud
table="reporte"
pk="id_reporte"
cols=["id_reporte","id_ciclo","id_administrador","fecha_de_generacion","tipo","descripcion","estado"]
render_crud(table, pk, cols)
