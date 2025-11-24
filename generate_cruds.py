# generate_cruds.py
from tables_def import TABLES
import os

TEMPLATE = open("crud_template_base.txt","r").read()  # vamos a usar template externalizado

os.makedirs("pages", exist_ok=True)

for filename, meta in TABLES.items():
    content = TEMPLATE
    content = content.replace("{{TABLE}}", meta["table"])
    content = content.replace("{{PK}}", meta["pk"])
    content = content.replace("{{FIELDS}}", str(meta["fields"]))
    content = content.replace("{{PERM_VIEW}}", meta["perm_view"])
    content = content.replace("{{PERM_CREATE}}", meta["perm_create"])
    content = content.replace("{{PERM_UPDATE}}", meta["perm_update"])
    content = content.replace("{{PERM_DELETE}}", meta["perm_delete"])
    dest = os.path.join("pages", filename + ".py")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print("Creado", dest)
