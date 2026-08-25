"""Script de migración: agrega columna foto_perfil y crea tablas compras/detalle_compras"""
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 1. Agregar foto_perfil a usuarios
    try:
        conn.execute(text("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT NULL"))
        conn.commit()
        print("Columna foto_perfil agregada a usuarios")
    except Exception as e:
        print(f"foto_perfil ya existe o error: {e}")

    # 2. Crear tabla compras
    try:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS compras ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  usuario_id INT NOT NULL,"
            "  fecha DATETIME DEFAULT CURRENT_TIMESTAMP,"
            "  total FLOAT NOT NULL,"
            "  estado VARCHAR(30) DEFAULT 'completada',"
            "  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)"
            ")"
        ))
        conn.commit()
        print("Tabla compras lista")
    except Exception as e:
        print(f"compras: {e}")

    # 3. Crear tabla detalle_compras
    try:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS detalle_compras ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  compra_id INT NOT NULL,"
            "  producto_id INT NOT NULL,"
            "  nombre_producto VARCHAR(100) NOT NULL,"
            "  precio_unitario FLOAT NOT NULL,"
            "  cantidad INT NOT NULL,"
            "  subtotal FLOAT NOT NULL,"
            "  FOREIGN KEY (compra_id) REFERENCES compras(id),"
            "  FOREIGN KEY (producto_id) REFERENCES productos(id)"
            ")"
        ))
        conn.commit()
        print("Tabla detalle_compras lista")
    except Exception as e:
        print(f"detalle_compras: {e}")

print("Migracion completada.")
