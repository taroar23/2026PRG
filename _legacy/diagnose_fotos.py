#!/usr/bin/env python3
"""
Script para verificar qué está guardado en la base de datos de fotos
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("DIAGNÓSTICO DE FOTOS DE PERFIL GUARDADAS")
print("=" * 80)

# Obtener todos los usuarios y sus fotos
cursor.execute("SELECT id, nombre, foto_perfil FROM usuarios;")
usuarios = cursor.fetchall()

for user_id, nombre, foto in usuarios:
    print(f"\n👤 Usuario: {nombre} (ID: {user_id})")
    if foto:
        print(f"  ✅ Tiene foto guardada")
        print(f"  📏 Tamaño: {len(foto)} caracteres")
        print(f"  🔍 Primeros 100 caracteres:")
        print(f"     {foto[:100]}")
        print(f"  🔍 Últimos 50 caracteres:")
        print(f"     {foto[-50:]}")
        
        # Verificar formato
        if foto.startswith("data:image/"):
            print(f"  ✅ Formato correcto: data URL")
            # Extraer MIME type
            mime_end = foto.find(";")
            mime_type = foto[5:mime_end] if mime_end > 0 else "desconocido"
            print(f"     MIME type: {mime_type}")
            
            # Verificar base64
            if ";base64," in foto:
                base64_start = foto.find(";base64,") + 8
                base64_data = foto[base64_start:]
                print(f"     Base64 válido: {len(base64_data)} caracteres")
                
                # Validar que sea base64 válido
                try:
                    import base64
                    decoded = base64.b64decode(base64_data)
                    print(f"     ✅ Base64 decodificable: {len(decoded)} bytes")
                except Exception as e:
                    print(f"     ❌ Error al decodificar base64: {e}")
            else:
                print(f"     ❌ No contiene ;base64,")
        else:
            print(f"  ❌ Formato incorrecto: no empieza con 'data:image/'")
    else:
        print(f"  ❌ Sin foto de perfil")

conn.close()
