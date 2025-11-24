import streamlit as st
from crud_template import render_crud
table="ahorro"
pk="id_ahorro"
cols=["id_ahorro","id_miembro","monto_actual","saldo_actual","fecha_de_actualizacion"]
render_crud(table, pk, cols)
