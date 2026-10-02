from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.ledger import verify_ledger

router = APIRouter(prefix="/api/ledger", tags=["ledger"])


@router.get("/verify")
def verify(db: Session = Depends(get_db)):
    return verify_ledger(db)
