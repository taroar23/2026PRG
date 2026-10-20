import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

EN_PRODUCCION = os.getenv("RENDER") == "true"

if all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    ca_path = os.path.join(base_dir, "ca.pem")
    connect_args = {"ssl": {"ca": ca_path}} if os.path.exists(ca_path) else {}
    engine = create_engine(DATABASE_URI, echo=False, pool_pre_ping=True, connect_args=connect_args)
    with engine.connect():
        pass
    print(f"✅ Conectado a MySQL en {DB_HOST}:{DB_PORT}/{DB_NAME}")
else:
    if EN_PRODUCCION:
        raise RuntimeError("Faltan variables de entorno DB_* en Render")
    print("⚠️ Sin config de MySQL, usando SQLite local (database.db)")
    db_path = os.path.join(base_dir, "database.db")
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )

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