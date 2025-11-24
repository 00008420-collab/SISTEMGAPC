import streamlit as st
from crud_template import render_crud
table="multa"
pk="id_multa"
cols=["id_multa","id_miembro","tipo","monto","descripcion","fecha","estado"]
render_crud(table, pk, cols)
