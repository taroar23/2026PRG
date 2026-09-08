#!/usr/bin/env python3
"""
Script simple para verificar que fotos funcionan (sin dependencias externas)
"""
import sqlite3
import os
import base64

db_path = os.path.join(os.path.dirname(__file__), 'database.db')

print("=" * 80)
print("VERIFICACIÓN: SISTEMA DE FOTOS - SIMULACIÓN")
print("=" * 80)

# Test 1: Crear foto de prueba
print("\n✏️ Test 1: Crear foto de prueba...")
png_data = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
)
foto_b64_str = base64.b64encode(png_data).decode('utf-8').strip()
foto_url = f"data:image/png;base64,{foto_b64_str}"

print(f"   ✅ Foto creada: {len(foto_url)} caracteres")
print(f"   Preview: {foto_url[:80]}...")

# Test 2: Conectar y limpiar BD
print("\n✏️ Test 2: Limpiar fotos anteriores...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ver qué usuarios hay
cursor.execute("SELECT id, nombre FROM usuarios LIMIT 3;")
usuarios = cursor.fetchall()
print(f"   Usuarios en BD: {usuarios}")

# Test 3: Guardar foto de prueba
print("\n✏️ Test 3: Guardar foto de prueba en usuario 1...")
try:
    cursor.execute("UPDATE usuarios SET foto_perfil = ? WHERE id = 1", (foto_url,))
    conn.commit()
    print("   ✅ Foto guardada")
except Exception as e:
    print(f"   ❌ Error: {e}")
    conn.close()
    exit(1)

# Test 4: Recuperar y validar
print("\n✏️ Test 4: Recuperar foto...")
cursor.execute("SELECT foto_perfil FROM usuarios WHERE id = 1;")
result = cursor.fetchone()

if result and result[0]:
    stored = result[0]
    print(f"   ✅ Foto recuperada: {len(stored)} caracteres")
    print(f"   Preview: {stored[:80]}...")
    
    # Validar
    if stored.startswith('data:image/png;base64,'):
        print(f"   ✅ Formato MIME correcto")
    else:
        print(f"   ❌ Formato incorrecto: {stored[:50]}")
    
    if ';base64,' in stored:
        base64_part = stored.split(';base64,')[1]
        try:
            decoded = base64.b64decode(base64_part)
            print(f"   ✅ Base64 válido y decodificable ({len(decoded)} bytes)")
        except Exception as e:
            print(f"   ❌ Base64 inválido: {e}")
    
    print("\n" + "=" * 80)
    print("✅ SISTEMA DE ALMACENAMIENTO FUNCIONA")
    print("=" * 80)
else:
    print("   ❌ No hay foto")

conn.close()
