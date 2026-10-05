from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

# Import models before creating tables
import models

# Import routers
from routers import (
    auth_router,
    product_router,
    cart_router,
    order_router,
    payment_router,
    admin_router
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Digital Product Store API",
    description="Full-stack Digital Product Store Backend",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# INCLUDE ROUTERS
# ============================================================

app.include_router(
    auth_router.router
)

app.include_router(
    product_router.router
)

app.include_router(
    cart_router.router
)

app.include_router(
    order_router.router
)

app.include_router(
    payment_router.router
)

app.include_router(
    admin_router.router
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Digital Product Store API is running"
    }