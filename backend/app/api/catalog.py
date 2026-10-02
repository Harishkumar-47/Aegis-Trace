from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.ai_model import AIModel
from app.models.user import User

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("")
def get_catalog(db: Session = Depends(get_db)):
    return {
        "users": [{"id": str(user.id), "email": user.email} for user in db.query(User).order_by(User.email).all()],
        "models": [{"id": str(model.id), "provider": model.provider, "name": model.model_name, "version": model.version} for model in db.query(AIModel).order_by(AIModel.provider, AIModel.model_name).all()],
    }
