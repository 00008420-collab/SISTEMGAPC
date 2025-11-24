# al comienzo del page
import streamlit as st
from auth.login import require_login
from auth.helpers import get_current_user

# bloque de protección de la página
user = require_login()
if not user:
    # require_login muestra el login box si no hay sesión
    st.stop()

# ahora continúa el contenido de la Page sabiendo que `user` existe

# pages/01_acta_crud.py
import streamlit as st
from crud_template import render_crud

table = "acta"
pk = "id_acta"
cols = ["id_acta","id_ciclo","tipo","fecha","descripcion"]

render_crud(table, pk, cols)
