from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from  routes import auth2 , shop , bookings ,ai
import models  # triggers table creation

# Import all routes

# Create all DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AiManager API", version="1.0.0")

# CORS — allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(auth2.router)
app.include_router(shop.router)
app.include_router(bookings.router)
app.include_router(ai.router)

# Serve frontend HTML files
# Make sure your frontend folder is at ../frontend relative to backend
import os
frontend_path = os.path.join(os.path.dirname(__file__), "..", "Frontend1")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/health")
def health():
    return {"status": "AiManager is running 🚀"}