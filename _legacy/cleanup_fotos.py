#!/usr/bin/env python3
"""
Script para limpiar fotos corruptas y analizar el problema
"""
import sqlite3
import os
import base64

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("LIMPIEZA Y VALIDACIÓN DE FOTOS")
print("=" * 80)

# Obtener todos los usuarios
cursor.execute("SELECT id, nombre, foto_perfil FROM usuarios;")
usuarios = cursor.fetchall()

corrupted_count = 0
valid_count = 0

for user_id, nombre, foto in usuarios:
    if not foto:
        continue
    
    # Validar foto
    try:
        if not foto.startswith("data:image/"):
            print(f"❌ {nombre} (ID: {user_id}): Formato inválido")
            cursor.execute("UPDATE usuarios SET foto_perfil = NULL WHERE id = ?", (user_id,))
            corrupted_count += 1
            continue
        
        if ";base64," not in foto:
            print(f"❌ {nombre} (ID: {user_id}): Sin base64")
            cursor.execute("UPDATE usuarios SET foto_perfil = NULL WHERE id = ?", (user_id,))
            corrupted_count += 1
            continue
        
        # Extraer y validar base64
        base64_start = foto.find(";base64,") + 8
        base64_data = foto[base64_start:]
        
        # Intentar decodificar
        decoded = base64.b64decode(base64_data)
        
        print(f"✅ {nombre} (ID: {user_id}): Válida ({len(decoded)} bytes)")
        valid_count += 1
        
    except Exception as e:
        print(f"❌ {nombre} (ID: {user_id}): Error - {e}")
        cursor.execute("UPDATE usuarios SET foto_perfil = NULL WHERE id = ?", (user_id,))
        corrupted_count += 1

conn.commit()
conn.close()

print(f"\n📊 Resumen:")
print(f"  ✅ Fotos válidas: {valid_count}")
print(f"  ❌ Fotos corruptas limpiadas: {corrupted_count}")
