import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from pathlib import Path

import os

# Configuración de Rutas
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

# Soporte para PostgreSQL (Supabase) via Environment Variable
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/antigravity.db")

# Si es Postgres de Supabase, SQLAlchemy necesita 'postgresql://' en lugar de 'postgres://' (que a veces devuelve Heroku/Supabase)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

DATA_DIR.mkdir(parents=True, exist_ok=True)

Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'tenants'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    owner_id = Column(String(36), nullable=True) # Linked to auth.users in Supabase
    subscription_tier = Column(String(20), default='free') # 'free' or 'pro'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    historical_data = relationship("HistoricalData", back_populates="tenant")

class HistoricalData(Base):
    __tablename__ = 'historical_data'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    sector = Column(String(50), nullable=False)
    item_key = Column(String(200), nullable=False)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON) # SQLite soporta JSON, Postgres usa JSONB automáticamente con sqlalchemy JSON
    
    tenant = relationship("Tenant", back_populates="historical_data")

# Engine y Sesión
# Ajuste para Supabase: pooling y ssl si es necesario
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
