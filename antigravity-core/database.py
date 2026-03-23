from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuracion del Motor (Usando SQLite local para el nucleo de Antigravity)
db_url = "sqlite:///antigravity-core/antigravity.db"
engine = create_engine(db_url, echo=False)

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True)
    name: str
    unit_type: str = "Unidades"
    current_cost: float = 0.0  # Nombrado exacto segun inventory_auditor.py
    price: float = 0.0
    stock: float = 0.0
    tenant_id: str = Field(index=True)

class PriceEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_sku: str = Field(index=True)
    costo_viejo: float
    costo_nuevo: float
    delta_erosion: float
    tenant_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TenantConfiguration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True)
    webhook_url: Optional[str] = None
    alert_threshold_leak: float = 20.0

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    # Test de ignicion
    create_db_and_tables()
    print("Boveda de Antigravity Inicializada")