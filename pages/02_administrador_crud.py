import streamlit as st
from crud_template import render_crud
table="administrador"
pk="id_administrador"
cols=["id_administrador","id_miembro","id_distrito","nombre","apellido","correo","rol"]
render_crud(table, pk, cols)
