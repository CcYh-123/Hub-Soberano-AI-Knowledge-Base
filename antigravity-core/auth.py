import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configuración desde entorno
SECRET_KEY = os.getenv("ANTIGRAVITY_SECRET_KEY", "sovereign_logic_shield_2026_!!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    tenant_id: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crea un JWT firmado con el tenant_id.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_tenant(token: str = Depends(oauth2_scheme)) -> str:
    """
    Middleware/Dependencia para extraer y validar el tenant_id del token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el acceso del Tenant",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id: str = payload.get("tenant_id")
        if tenant_id is None:
            raise credentials_exception
        return tenant_id
    except jwt.PyJWTError:
        raise credentials_exception
