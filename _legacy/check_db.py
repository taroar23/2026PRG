#!/usr/bin/env python3
import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("ESTRUCTURA DE LA TABLA USUARIOS")
print("=" * 70)

# Ver columnas
cursor.execute("PRAGMA table_info(usuarios);")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]}: {col[2]} (null: {col[3]}, default: {col[4]}, pk: {col[5]})")

print("\n" + "=" * 70)
print("DATOS DE USUARIOS")
print("=" * 70)

# Ver usuarios
cursor.execute("SELECT COUNT(*) FROM usuarios;")
count = cursor.fetchone()[0]
print(f"Total de usuarios: {count}\n")

cursor.execute("SELECT id, nombre, nombre_usuario, email, foto_perfil FROM usuarios;")
users = cursor.fetchall()
for user in users:
    id_, name, username, email, foto = user
    foto_status = "SI" if foto else "NO"
    print(f"ID: {id_}")
    print(f"  Nombre: {name}")
    print(f"  Usuario: {username}")
    print(f"  Email: {email}")
    print(f"  Foto de perfil: {foto_status}")
    if foto:
        print(f"  Preview: {foto[:100]}...")
    print()

conn.close()
