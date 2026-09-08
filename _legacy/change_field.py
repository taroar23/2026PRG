#!/usr/bin/env python3
"""
Cambiar campo a LONGTEXT
"""
import pymysql

print("Conectando a MySQL y cambiando tipo de campo...")

try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='empresa_cli1',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    print("Ejecutando ALTER TABLE...")
    cursor.execute("""
        ALTER TABLE usuarios 
        MODIFY COLUMN foto_perfil LONGTEXT NULL
    """)
    conn.commit()
    
    print("✅ Campo cambiado a LONGTEXT")
    
    # Verificar
    cursor.execute("SHOW COLUMNS FROM usuarios WHERE Field='foto_perfil'")
    result = cursor.fetchone()
    print(f"Tipo actual: {result[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
