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

app.include_router(auth.router)
app.include_router(workspace.router)
app.include_router(budget.router)


@app.get("/")
async def root():
    return {"message": "Welcome to WiseLab API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
