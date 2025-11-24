import streamlit as st
from crud_template import render_crud
table="pago"
pk="id_pago"
cols=["id_pago","id_prestamo","fecha","monto","interes_pagado","multa_aplicada","saldo_restante","id_cuota"]
render_crud(table, pk, cols)
