import streamlit as st
from crud_template import render_crud
table="prestamo"
pk="id_prestamo"
cols=["id_prestamo","id_promotora","id_ciclo","id_miembro","monto","intereses","saldo_restante","estado","plazo_meses","total_cuotas"]
render_crud(table, pk, cols)
