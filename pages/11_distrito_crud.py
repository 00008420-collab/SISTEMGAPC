import streamlit as st
from crud_template import render_crud
table="distrito"
pk="id_distrito"
cols=["id_distrito","id_grupo","nombre","lugar"]
render_crud(table, pk, cols)
