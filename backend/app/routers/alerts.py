from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertLog, User
from app.schemas import AlertOut
from app.security import get_current_user, require_client_access

router = APIRouter(prefix="/clients/{client_id}/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertOut])
def list_alerts(client_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_client_access(client_id, current_user)
    return (
        db.query(AlertLog)
        .filter(AlertLog.client_id == client_id)
        .order_by(AlertLog.triggered_at.desc())
        .limit(50)
        .all()
    )
