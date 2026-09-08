#!/usr/bin/env python3
"""
Script para limpiar y verificar todas las fotos
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("VERIFICACIÓN DE TODOS LOS USUARIOS")
print("=" * 80)

# Obtener TODOS los usuarios con foto
cursor.execute("SELECT id, nombre, foto_perfil FROM usuarios WHERE foto_perfil IS NOT NULL;")
usuarios = cursor.fetchall()

print(f"\nTotal de usuarios con foto: {len(usuarios)}")

for user_id, nombre, foto in usuarios:
    print(f"\n👤 Usuario: {nombre} (ID: {user_id})")
    print(f"   Foto length: {len(foto) if foto else 0}")
    if foto:
        print(f"   First 100 chars: {foto[:100]}")
        if foto.startswith('data:image/'):
            print(f"   ✅ Formato válido")
        else:
            print(f"   ❌ Formato INCORRECTO: {foto[:50]}")

# Mostrar estructura de tabla
print("\n" + "=" * 80)
print("ESTRUCTURA DE TABLA")
print("=" * 80)
cursor.execute("PRAGMA table_info(usuarios);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

conn.close()
