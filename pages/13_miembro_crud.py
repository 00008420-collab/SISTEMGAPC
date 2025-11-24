import streamlit as st
from crud_template import render_crud
table="miembro"
pk="id_miembro"
cols=["id_miembro","id_tipo_usuario","apellido","dui","direccion"]
render_crud(table, pk, cols)
