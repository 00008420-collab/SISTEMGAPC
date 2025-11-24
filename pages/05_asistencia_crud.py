import streamlit as st
from crud_template import render_crud
table="asistencia"
pk="id_asistencia"
cols=["id_asistencia","id_miembro","id_multa","motivo","presente_ausente"]
render_crud(table, pk, cols)
