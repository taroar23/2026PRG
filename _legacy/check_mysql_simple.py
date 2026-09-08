#!/usr/bin/env python3
"""
Script simple para verificar la BD MySQL
"""
import os

print("=" * 80)
print("VERIFICACIÓN DE BASE DE DATOS MYSQL")
print("=" * 80)

# Ver variables de entorno
print(f"\n📊 Leyendo archivo .env...")

env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, val = line.split('=', 1)
                    if 'DB' in key or 'PASSWORD' not in key:
                        print(f"   {key}={val}")
else:
    print(f"   ❌ No existe archivo .env")

try:
    import pymysql
    
    # Intentar conectar
    print(f"\n🔌 Intentando conectar a MySQL...")
    
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='empresa_cli1',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    print(f"   ✅ Conectado exitosamente\n")
    
    # Ver todos los usuarios con info de foto
    print(f"👥 USUARIOS EN MYSQL:")
    cursor.execute("""
        SELECT id, nombre, nombre_usuario, email, 
               IF(foto_perfil IS NULL, 0, LENGTH(foto_perfil)) as foto_len,
               IF(foto_perfil IS NOT NULL AND foto_perfil LIKE 'data:image/%', 'VÁLIDA', 'INVÁLIDA') as foto_status
        FROM usuarios
    """)
    
    usuarios = cursor.fetchall()
    for row in usuarios:
        user_id, nombre, username, email, foto_len, foto_status = row
        print(f"   {user_id}: {nombre:15} | {email:30} | Foto: {foto_len:6} bytes | {foto_status}")
    
    # Ver específicamente el usuario con r@gmail.com
    print(f"\n🔍 Buscando usuario 'r':")
    cursor.execute("SELECT id, nombre, email, foto_perfil FROM usuarios WHERE nombre='r' OR email LIKE '%r@%' LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        user_id, nombre, email, foto = result
        print(f"   ✅ Encontrado: ID={user_id}, Nombre={nombre}, Email={email}")
        
        if foto:
            print(f"\n   📋 FOTO GUARDADA:")
            print(f"      Longitud: {len(foto)} caracteres")
            print(f"      Primeros 150 caracteres:")
            print(f"      {foto[:150]}")
            print(f"\n      Últimos 100 caracteres:")
            print(f"      {foto[-100:]}")
            
            # Validar formato
            if foto.startswith('data:image/'):
                print(f"\n      ✅ FORMATO VÁLIDO (data URL)")
                if 'base64' in foto:
                    print(f"      ✅ Contiene base64")
                else:
                    print(f"      ❌ NO contiene base64")
            else:
                print(f"\n      ❌ FORMATO INVÁLIDO")
        else:
            print(f"   ❌ Sin foto de perfil")
    else:
        print(f"   ❌ Usuario no encontrado")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print(f"   ❌ pymysql no instalado - pip install pymysql")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"      Verifica que MySQL está corriendo en localhost:3306")
