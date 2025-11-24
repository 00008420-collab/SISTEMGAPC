import streamlit as st
from crud_template import render_crud
table="caja"
pk="id_caja"
cols=["id_caja","id_ciclo","id_ahorro","id_prestamo","id_pago","saldo_inicial","ingresos","egresos","saldo_final"]
render_crud(table, pk, cols)
