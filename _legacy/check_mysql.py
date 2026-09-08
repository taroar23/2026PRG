#!/usr/bin/env python3
"""
Script para verificar la BD MySQL y ver qué se guardó
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

print("=" * 80)
print("VERIFICACIÓN DE BASE DE DATOS MYSQL")
print("=" * 80)

# Ver variables de conexión
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

print(f"\n📊 Configuración de BD:")
print(f"   Host: {db_host}:{db_port}")
print(f"   User: {db_user}")
print(f"   Database: {db_name}")

try:
    import pymysql
    
    # Conectar a MySQL
    conn = pymysql.connect(
        host=db_host,
        port=int(db_port),
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Ver todos los usuarios
    print(f"\n👥 USUARIOS EN BD MYSQL:")
    cursor.execute("SELECT id, nombre, nombre_usuario, email, LENGTH(foto_perfil) as foto_len FROM usuarios;")
    usuarios = cursor.fetchall()
    
    for user_id, nombre, nombre_usuario, email, foto_len in usuarios:
        foto_status = f"✅ ({foto_len} bytes)" if foto_len and foto_len > 0 else "❌ SIN FOTO"
        print(f"   {user_id}: {nombre:12} | {nombre_usuario:12} | {email:30} | {foto_status}")
    
    # Buscar usuario 'r' específicamente
    print(f"\n🔍 BÚSQUEDA: Usuario con email que contenga 'r@':")
    cursor.execute("SELECT id, nombre, email, foto_perfil FROM usuarios WHERE email LIKE '%r@%' LIMIT 1;")
    result = cursor.fetchone()
    
    if result:
        user_id, nombre, email, foto = result
        print(f"   ✅ Usuario encontrado: {nombre} ({email})")
        if foto:
            print(f"   Foto length: {len(foto)}")
            print(f"   Primeros 150 caracteres:")
            print(f"   {foto[:150]}")
            if foto.startswith('data:image/'):
                print(f"   ✅ Formato correcto")
            else:
                print(f"   ❌ Formato incorrecto: comienza con {foto[:50]}")
        else:
            print(f"   ❌ Sin foto")
    else:
        print(f"   ❌ No encontrado")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print(f"\n❌ pymysql no está instalado")
    print(f"   Instala con: pip install pymysql")
except Exception as e:
    print(f"\n❌ Error al conectar a MySQL: {e}")
    print(f"   Asegúrate de que MySQL está corriendo")
    print(f"   Y que las credenciales en .env son correctas")
