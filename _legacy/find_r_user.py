#!/usr/bin/env python3
"""
Script para buscar al usuario con email r@gmail.com
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("BÚSQUEDA: usuario con email r@gmail.com")
print("=" * 80)

# Búsqueda exacta
cursor.execute("SELECT id, nombre, nombre_usuario, email, foto_perfil FROM usuarios WHERE email = 'r@gmail.com';")
result = cursor.fetchone()

if result:
    user_id, nombre, nombre_usuario, email, foto = result
    print(f"\n✅ Usuario encontrado:")
    print(f"   ID: {user_id}")
    print(f"   Nombre: {nombre}")
    print(f"   Usuario: {nombre_usuario}")
    print(f"   Email: {email}")
    print(f"   Foto: {'SÍ' if foto else 'NO'}")
    
    if foto:
        print(f"\n   📋 DETALLES DE LA FOTO:")
        print(f"   Longitud: {len(foto)} caracteres")
        print(f"   Primeros 150 chars: {foto[:150]}")
        print(f"   Últimos 100 chars: {foto[-100:]}")
else:
    print(f"\n❌ No hay usuario con email 'r@gmail.com'")
    
    # Mostrar todos los emails
    print(f"\n📧 Emails registrados:")
    cursor.execute("SELECT id, nombre, email FROM usuarios;")
    users = cursor.fetchall()
    for uid, name, email in users:
        print(f"   {uid}: {name} ({email})")

conn.close()
