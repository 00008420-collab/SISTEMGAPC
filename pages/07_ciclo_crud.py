import streamlit as st
from crud_template import render_crud
table="ciclo"
pk="id_ciclo"
cols=["id_ciclo","fecha_inicio","fecha_fin","estado","total_utilidad"]
render_crud(table, pk, cols)
