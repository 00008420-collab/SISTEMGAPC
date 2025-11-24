# auth/login.py (fragmento importante)
from db import run_query, get_user_by_username
import streamlit as st
import hashlib

def verify_password_sha256(plain_text, stored_hash):
    # si usas SHA2/sha256: comparar hex digest
    h = hashlib.sha256(plain_text.encode("utf-8")).hexdigest()
    return h == stored_hash

def login_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return None, "Usuario no encontrado."
    # tu columna se llama password_hash (ver tu tabla)
    stored = user.get("password_hash") or user.get("password")
    # Detecta si el hash está en formato 'scrypt:' u otro; si es sha256 comparas
    if stored is None:
        return None, "Usuario sin contraseña guardada."
    # Ejemplo simple: si tu password_hash es hex sha256:
    if verify_password_sha256(password, stored):
        return user, None
    # Si usas otros schemata de hash (scrypt / bcrypt) necesitarás la librería adecuada
    return None, "Contraseña incorrecta."
