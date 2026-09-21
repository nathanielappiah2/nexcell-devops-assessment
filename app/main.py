import os

import psycopg2
import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/nexcell"
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        redis.Redis.from_url(REDIS_URL).ping()

        connection = psycopg2.connect(DATABASE_URL)
        connection.close()

        return {"status": "ready"}

    except Exception as exc:
        raise HTTPException(status_code=503, detail="Dependency unavailable") from exc
