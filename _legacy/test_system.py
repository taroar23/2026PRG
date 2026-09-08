#!/usr/bin/env python3
"""
Script para verificar que el sistema de fotos está funcionando correctamente
"""
import sqlite3
import os
import base64
import sys

# Agregar ruta para imports
sys.path.insert(0, os.path.dirname(__file__))

from models import Usuario
from database import SessionLocal

db_path = os.path.join(os.path.dirname(__file__), 'database.db')

print("=" * 80)
print("VERIFICACIÓN FINAL: SISTEMA DE FOTOS DE PERFIL")
print("=" * 80)

# Test 1: Crear una foto de prueba válida
print("\n✏️ Test 1: Crear foto de prueba...")
try:
    # Crear un pixel rojo 1x1 en PNG
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
    )
    
    # Crear data URL
    foto_b64_str = base64.b64encode(png_data).decode('utf-8').strip()
    foto_url = f"data:image/png;base64,{foto_b64_str}"
    
    # Validar
    assert foto_url.startswith('data:image/png;base64,'), "Data URL inválida"
    assert len(foto_url) > 100, "Data URL demasiado corta"
    print(f"   ✅ Foto de prueba creada ({len(foto_url)} caracteres)")
    print(f"   Preview: {foto_url[:80]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Guardar en base de datos
print("\n✏️ Test 2: Guardar foto en base de datos...")
try:
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.id == 1).first()
    if user:
        user.foto_perfil = foto_url
        db.commit()
        print(f"   ✅ Foto guardada para usuario: {user.nombre}")
    else:
        print(f"   ❌ Usuario no encontrado")
        db.close()
        sys.exit(1)
    db.close()
except Exception as e:
    print(f"   ❌ Error al guardar: {e}")
    sys.exit(1)

# Test 3: Recuperar y validar
print("\n✏️ Test 3: Recuperar y validar foto...")
try:
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.id == 1).first()
    if user and user.foto_perfil:
        stored_foto = user.foto_perfil
        print(f"   ✅ Foto recuperada ({len(stored_foto)} caracteres)")
        
        # Validar formato
        assert stored_foto.startswith('data:image/'), "Formato inválido"
        assert ';base64,' in stored_foto, "Sin base64"
        
        # Validar base64
        base64_part = stored_foto.split(';base64,')[1]
        decoded = base64.b64decode(base64_part)
        print(f"   ✅ Base64 válido ({len(decoded)} bytes decodificados)")
        print(f"   ✅ SISTEMA DE FOTOS FUNCIONA CORRECTAMENTE")
    else:
        print(f"   ❌ Foto no encontrada en BD")
        db.close()
        sys.exit(1)
    db.close()
except Exception as e:
    print(f"   ❌ Error al validar: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ TODOS LOS TESTS PASARON - SISTEMA FUNCIONANDO")
print("=" * 80)
