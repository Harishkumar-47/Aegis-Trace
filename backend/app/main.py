from fastapi import FastAPI

from app.api.decisions import router as decisions_router

app = FastAPI(title="Aegis Trace API")
app.include_router(decisions_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aegis-trace-backend"}
