#!/usr/bin/env python3
"""
Script para ver TODOS los usuarios y sus fotos
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("TODOS LOS USUARIOS Y SUS FOTOS")
print("=" * 80)

cursor.execute("SELECT id, nombre, nombre_usuario, email, foto_perfil FROM usuarios;")
users = cursor.fetchall()

print(f"\nTotal de usuarios: {len(users)}\n")

for user_id, nombre, nombre_usuario, email, foto in users:
    print(f"ID: {user_id} | Nombre: {nombre:12} | Usuario: {nombre_usuario:12} | Email: {email}")
    if foto:
        print(f"   ✅ FOTO: {len(foto)} caracteres")
        print(f"      {foto[:100]}...")
    else:
        print(f"   ❌ Sin foto")
    print()

conn.close()
