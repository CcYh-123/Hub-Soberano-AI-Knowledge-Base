import os

base_path = 'C:/Users/Lenovo/Antigravity_Home/Proyecto_Antigravity'
for root, dirs, files in os.walk(base_path):
    if 'node_modules' in root or '.git' in root:
        continue
    for file in files:
        fl = file.lower()
        if '06' in fl and '03' in fl:
            print("FOUND DATE:", os.path.join(root, file))
        if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
            print("FOUND BD:", os.path.join(root, file))
        if 'precio' in fl or 'mercado' in fl or 'market' in fl or 'guardian' in fl or 'agro' in fl:
            print("FOUND KEYWORD:", os.path.join(root, file))
