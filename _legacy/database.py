import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Cargar .env desde la misma carpeta del archivo
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

DATABASE_URI = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Intentar conectar a MySQL, si falla, usar SQLite
try:
    engine = create_engine(DATABASE_URI, echo=False)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception:
    db_path = os.path.join(base_dir, "database.db")
    DATABASE_URI = f"sqlite:///{db_path}"
    engine = create_engine(DATABASE_URI, echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import models
Base.metadata.create_all(bind=engine)