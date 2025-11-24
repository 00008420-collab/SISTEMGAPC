# app.py
"""
SGAPC - Main menu (custom)
Reemplaza totalmente el app.py actual por este.

Dependencias:
- Debe existir un módulo db.py en el repo que exponga:
    - test_connection() -> (True/False, message)
    - get_table_names() -> list[str]  (o raise/return None en error)
Si no existen, la app seguirá funcionando pero mostrará mensajes de error.

Pages:
- Lee archivos en ./pages/*.py y usa el nombre de archivo (sin .py) como page id,
  por ejemplo '01_acta_crud' para redireccionar a ?page=01_acta_crud
"""

from pathlib import Path
import os
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# Importar funciones de db (debe existir db.py)
try:
    from db import test_connection, get_table_names
except Exception:
    # Si no está disponible, definimos stubs que devuelven error para que la app cargue
    def test_connection():
        return False, "db
