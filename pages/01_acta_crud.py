# pages/01_acta_crud.py
import streamlit as st
from crud_template import render_crud

table = "acta"
pk = "id_acta"
cols = ["id_acta","id_ciclo","tipo","fecha","descripcion"]

render_crud(table, pk, cols)
