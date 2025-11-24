import streamlit as st
from crud_template import render_crud
table="reunion"
pk="id_reunion"
cols=["id_reunion","id_grupo","id_asistencia","fecha","dia","lugar","extraordinario_ordinario"]
render_crud(table, pk, cols)
