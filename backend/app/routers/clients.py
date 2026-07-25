from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, User, UserRole
from app.schemas import ClientCreate, ClientOut
from app.security import get_current_user, require_client_access

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=List[ClientOut])
def list_clients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.agency_admin:
        return db.query(Client).all()
    # client_user only sees their own client
    return db.query(Client).filter(Client.id == current_user.client_id).all()


@router.post("/", response_model=ClientOut)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.agency_admin:
        raise HTTPException(status_code=403, detail="Only agency admins can create clients")
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
def get_client(client_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_client_access(client_id, current_user)
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
