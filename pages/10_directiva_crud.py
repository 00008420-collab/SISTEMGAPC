import streamlit as st
from crud_template import render_crud
table="directiva"
pk="id_directiva"
cols=["id_directiva","id_grupo","fecha_inicio","fecha_fin","activa_inactiva"]
render_crud(table, pk, cols)
