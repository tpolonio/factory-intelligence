from fastapi import FastAPI
from app.api.v1.router import router
import app.models

app = FastAPI(
    title="Factory Intelligence API",
    description="Industrial analytics API for quality test results and production OEE tracking",
    version="0.1.0",

)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Factory Intelligence API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

