import streamlit as st
from crud_template import render_crud
table="cuota"
pk="id_cuota"
cols=["id_cuota","id_prestamo","fecha_de_vencimiento","numero","monto_capital","monto_interes","monto_total","estado"]
render_crud(table, pk, cols)
