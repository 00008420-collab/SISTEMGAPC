# tables_def.py
TABLES = {
    "01_acta_crud": {
        "table": "acta",
        "pk": "id_acta",
        "fields": ["id_ciclo","tipo","fecha","descripcion"],
        "perm_view": "ver_acta",
        "perm_create": "crear_acta",
        "perm_update": "editar_acta",
        "perm_delete": "borrar_acta"
    },
    "02_administrador_crud": {
        "table": "administrador",
        "pk": "id_administrador",
        "fields": ["id_miembro","id_distrito","nombre","apellido","correo","rol"],
        "perm_view": "ver_administrador",
        "perm_create": "crear_administrador",
        "perm_update": "editar_administrador",
        "perm_delete": "borrar_administrador"
    },
    # ... agrega las 17 definiciones restantes siguiendo el mismo patrón ...
}
