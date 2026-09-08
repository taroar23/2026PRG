#!/usr/bin/env python3
"""
Limpiar la foto truncada anterior
"""
import pymysql

print("Limpiando foto truncada...")

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
    
    # Limpiar la foto del usuario 'r'
    cursor.execute("UPDATE usuarios SET foto_perfil = NULL WHERE nombre = 'r'")
    conn.commit()
    
    print("✅ Foto truncada eliminada")
    print("\n📋 Ahora cuando subas una nueva foto, se guardará completa")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
