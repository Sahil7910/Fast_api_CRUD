from urllib.request import Request

from fastapi import FastAPI
from app.routers import Items, Clock_In
from fastapi.responses import JSONResponse

app = FastAPI()

# Include routers
app.include_router(Items.router)
app.include_router(Clock_In.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI CRUD App"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."}
    )