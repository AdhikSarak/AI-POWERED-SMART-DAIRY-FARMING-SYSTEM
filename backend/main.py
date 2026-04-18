from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.database import create_tables
from backend.routers import auth, cows, health, milk, recommendations, chatbot, agentic, billing, reports, admin

app = FastAPI(
    title="Smart Dairy Farming System",
    description="Deep Learning-Based Integrated Smart Dairy Farming System for Cattle Health Monitoring and Milk Quality Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if not exists
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register all routers
app.include_router(auth.router,            prefix="/auth",            tags=["Authentication"])
app.include_router(cows.router,            prefix="/cows",            tags=["Cow Management"])
app.include_router(health.router,          prefix="/health",          tags=["Health Monitoring"])
app.include_router(milk.router,            prefix="/milk",            tags=["Milk Quality"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(chatbot.router,         prefix="/chatbot",         tags=["AI Chatbot"])
app.include_router(agentic.router,         prefix="/agentic",         tags=["Agentic AI"])
app.include_router(billing.router,         prefix="/billing",         tags=["Billing & Collection"])
app.include_router(reports.router,         prefix="/reports",         tags=["Reports"])
app.include_router(admin.router,           prefix="/admin",           tags=["Admin Panel"])


@app.on_event("startup")
def on_startup():
    create_tables()
    print("Database tables created successfully.")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Smart Dairy Farming System API",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health-check", tags=["Root"])
def health_check():
    return {"status": "ok"}
