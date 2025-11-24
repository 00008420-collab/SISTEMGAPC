# auth/config.py
"""
Configuración de autenticación.
Ajusta AUTH_TABLE, USER_COL, PASS_COL según tu BD.
Si usas contraseñas en texto plano, deja PASSWORD_HASH = "plain".
Si usas hash tipo bcrypt, ajusta a "bcrypt" y asegúrate de instalar bcrypt en requirements.
"""

PROJECT_PDF_PATH = "/mnt/data/Proyecto final rev.pdf"  # ruta del pdf que subiste (opcional)

# Ajusta según tu BD
AUTH_TABLE = "administrador"
AUTH_USER_COL = "correo"   # nombre de columna que contiene el usuario / email
AUTH_PASS_COL = "password" # nombre de columna que contiene la contraseña

PASSWORD_HASH = "plain"  # "plain" o "bcrypt"
SESSION_KEY = "auth_user"
