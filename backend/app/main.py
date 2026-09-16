import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analytics import router as analytics_router

app = FastAPI(title="Customer Segmentation API")

allowed_origins = ["http://localhost:5173"]
allowed_origins.extend(
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(allowed_origins)),
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(analytics_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "customer-segmentation-api",
    }
