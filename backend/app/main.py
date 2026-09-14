from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analytics import router as analytics_router

app = FastAPI(title="Customer Segmentation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
