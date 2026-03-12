from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.routers import admin_auth, chat, documents, tenants, analytics, external

app = FastAPI(
    title="ForteAI Bot",
    description="Multi-tenant AI assistant with Help Mode (RAG) and Data Mode (Function Calling)",
    version="0.1.0",
)

# CORS — allow the widget to call from any host app
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(admin_auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(tenants.router)
app.include_router(analytics.router)
app.include_router(external.router)

# Serve extracted document images
images_dir = os.path.join(os.path.dirname(__file__), "..", "data", "images")
os.makedirs(images_dir, exist_ok=True)
app.mount("/data/images", StaticFiles(directory=images_dir), name="images")

# Serve the widget static files
widget_dir = os.path.join(os.path.dirname(__file__), "..", "..", "widget")
if os.path.exists(widget_dir):
    app.mount("/widget", StaticFiles(directory=widget_dir), name="widget")

# Serve the admin dashboard
admin_dir = os.path.join(os.path.dirname(__file__), "..", "..", "admin")
if os.path.exists(admin_dir):
    app.mount("/admin", StaticFiles(directory=admin_dir, html=True), name="admin")


@app.get("/")
async def root():
    return {
        "name": "ForteAI Bot",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
