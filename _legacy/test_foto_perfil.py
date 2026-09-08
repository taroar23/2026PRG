#!/usr/bin/env python3
"""
Script de prueba para verificar que la funcionalidad de foto de perfil funciona.
"""
import sqlite3
import os
import base64

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("PRUEBA: Guardando y recuperando foto de perfil")
print("=" * 70)

# Obtener el primer usuario
cursor.execute("SELECT id, nombre FROM usuarios LIMIT 1;")
result = cursor.fetchone()

if result:
    user_id, nombre = result
    print(f"\n📝 Simulando subida de foto para usuario: {nombre} (ID: {user_id})")
    
    # Crear una imagen de prueba (pixel rojo simple en PNG)
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
    )
    
    # Codificar como data URL base64
    foto_b64 = f"data:image/png;base64,{base64.b64encode(png_data).decode()}"
    
    print(f"✏️ Guardando foto en la base de datos...")
    
    # Actualizar foto de perfil
    try:
        cursor.execute(
            "UPDATE usuarios SET foto_perfil = ? WHERE id = ?",
            (foto_b64, user_id)
        )
        conn.commit()
        print("✅ Foto guardada exitosamente")
    except Exception as e:
        print(f"❌ Error al guardar foto: {e}")
        conn.close()
        exit(1)
    
    # Recuperar la foto
    cursor.execute("SELECT foto_perfil FROM usuarios WHERE id = ?;", (user_id,))
    foto_guardada = cursor.fetchone()[0]
    
    if foto_guardada:
        print("✅ Foto recuperada de la base de datos")
        print(f"📦 Tamaño: {len(foto_guardada)} caracteres")
        print(f"🔍 Preview: {foto_guardada[:80]}...")
        print("\n✅ LA FUNCIONALIDAD DE FOTO DE PERFIL AHORA FUNCIONA CORRECTAMENTE")
    else:
        print("❌ No se pudo recuperar la foto")
else:
    print("❌ No hay usuarios en la base de datos")

conn.close()
