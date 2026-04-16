"""FastAPI application for UAV Flight Optimizer Routing Engine."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.optimize import router as optimize_router

app = FastAPI(
    title="UAV Flight Optimizer - Routing Engine",
    description="Energy-weighted 3D pathfinding for UAV flight route optimization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(optimize_router, prefix="/api/v1", tags=["optimization"])


@app.get("/")
async def root():
    return {
        "service": "UAV Flight Optimizer - Routing Engine",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
