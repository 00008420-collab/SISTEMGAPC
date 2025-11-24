import streamlit as st
from crud_template import render_crud
table="promotora"
pk="id_promotora"
cols=["id_promotora","id_administrador","nombre","apellido","telefono","correo","distrito"]
render_crud(table, pk, cols)
