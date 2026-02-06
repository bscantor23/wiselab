from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import auth, budget, workspace

app = FastAPI(
    title="WiseLab Financial Planning API",
    description="Backend for the Personal Financial Planning System",
    version="0.1.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.routes import auth, budget, workspace
from fastapi import APIRouter

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(workspace.router)
api_router.include_router(budget.router)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to WiseLab API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
