#!/usr/bin/env python3
"""
Script para ver exactamente qué se guardó para el usuario 'r'
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("DIAGNÓSTICO: QUÉ SE GUARDÓ PARA EL USUARIO 'r'")
print("=" * 80)

# Buscar usuario por email
cursor.execute("SELECT id, nombre, nombre_usuario, email, foto_perfil FROM usuarios WHERE email LIKE '%r@%' OR nombre = 'r' OR nombre_usuario = 'r';")
users = cursor.fetchall()

print(f"\nUsuarios encontrados: {len(users)}")

for user_id, nombre, nombre_usuario, email, foto in users:
    print(f"\n👤 Usuario encontrado:")
    print(f"   ID: {user_id}")
    print(f"   Nombre: {nombre}")
    print(f"   Usuario: {nombre_usuario}")
    print(f"   Email: {email}")
    print(f"   Foto guardada: {'SÍ' if foto else 'NO'}")
    
    if foto:
        print(f"\n   📋 CONTENIDO DE LA FOTO:")
        print(f"   Longitud total: {len(foto)} caracteres")
        print(f"   Primeros 150 caracteres:")
        print(f"   {foto[:150]}")
        print(f"\n   Últimos 100 caracteres:")
        print(f"   {foto[-100:]}")
        
        # Validar
        if foto.startswith('data:image/'):
            print(f"\n   ✅ Formato correcto (data URL)")
            if ';base64,' in foto:
                print(f"   ✅ Contiene base64")
            else:
                print(f"   ❌ NO contiene base64")
        else:
            print(f"\n   ❌ FORMATO INCORRECTO")
            print(f"   Comienza con: {foto[:50]}")

conn.close()
