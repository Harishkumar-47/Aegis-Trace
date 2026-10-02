from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.decisions import router as decisions_router
from app.api.catalog import router as catalog_router
from app.api.ledger import router as ledger_router
from app.db.session import get_db

app = FastAPI(title="Aegis Trace API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])
app.include_router(decisions_router)
app.include_router(catalog_router)
app.include_router(ledger_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aegis-trace-backend"}


@app.get("/api/status")
def system_status(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"api": "ready", "database": "connected", "phase": 1}
