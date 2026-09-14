from fastapi import FastAPI

app = FastAPI(title="Aegis Trace API")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aegis-trace-backend"}
