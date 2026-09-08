#!/usr/bin/env python3
"""
Script para arreglar la estructura de la tabla usuarios en MySQL
"""
import pymysql

print("=" * 80)
print("ARREGLANDO ESTRUCTURA DE BD MYSQL")
print("=" * 80)

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
    
    print(f"\n📊 Verificando tipo de campo actual...")
    cursor.execute("SHOW COLUMNS FROM usuarios WHERE Field='foto_perfil';")
    result = cursor.fetchone()
    
    if result:
        print(f"   Campo actual: {result[1]}")
        
        if 'VARCHAR' in result[1]:
            print(f"\n⚠️  Campo es VARCHAR - demasiado pequeño para imágenes")
            print(f"\n🔄 Cambiando a LONGTEXT...")
            
            cursor.execute("ALTER TABLE usuarios MODIFY COLUMN foto_perfil LONGTEXT;")
            conn.commit()
            
            print(f"   ✅ Campo modificado a LONGTEXT")
            
            # Verificar
            cursor.execute("SHOW COLUMNS FROM usuarios WHERE Field='foto_perfil';")
            result = cursor.fetchone()
            print(f"   Tipo actual: {result[1]}")
        else:
            print(f"   ✅ Ya es {result[1]} (suficiente)")
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ MIGRACIÓN COMPLETADA")
    
except Exception as e:
    print(f"❌ Error: {e}")
