#!/usr/bin/env python3
import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("AGREGANDO COLUMNA foto_perfil A LA TABLA usuarios")
print("=" * 70)

try:
    # Agregar la columna foto_perfil si no existe
    cursor.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT;")
    conn.commit()
    print("✅ Columna 'foto_perfil' agregada exitosamente")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("⚠️ La columna 'foto_perfil' ya existe")
    else:
        print(f"❌ Error: {e}")

# Verificar que la columna existe
cursor.execute("PRAGMA table_info(usuarios);")
columns = cursor.fetchall()
print("\nColumnas actuales en la tabla usuarios:")
for col in columns:
    print(f"  - {col[1]}: {col[2]}")

conn.close()
print("\n✅ Migración completada")
