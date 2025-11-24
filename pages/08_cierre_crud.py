import streamlit as st
from crud_template import render_crud
table="cierre"
pk="id_cierre"
cols=["id_cierre","id_ciclo","descripcion","fecha"]
render_crud(table, pk, cols)
