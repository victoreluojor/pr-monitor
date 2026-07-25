from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Keyword, User
from app.schemas import KeywordCreate, KeywordOut
from app.security import get_current_user, require_client_access

router = APIRouter(prefix="/clients/{client_id}/keywords", tags=["keywords"])


@router.get("/", response_model=List[KeywordOut])
def list_keywords(client_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_client_access(client_id, current_user)
    return db.query(Keyword).filter(Keyword.client_id == client_id).all()


@router.post("/", response_model=KeywordOut)
def add_keyword(
    client_id: str,
    payload: KeywordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_client_access(client_id, current_user)
    keyword = Keyword(client_id=client_id, **payload.model_dump())
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword


@router.delete("/{keyword_id}")
def delete_keyword(
    client_id: str,
    keyword_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_client_access(client_id, current_user)
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id, Keyword.client_id == client_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(keyword)
    db.commit()
    return {"deleted": True}
