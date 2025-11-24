import streamlit as st
from crud_template import render_crud
table="aporte"
pk="id_aporte"
cols=["id_aporte","id_miembro","id_reunion","monto","fecha","tipo"]
render_crud(table, pk, cols)
