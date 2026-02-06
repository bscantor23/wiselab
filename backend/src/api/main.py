from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WiseLab Financial Planning API",
    description="Backend for the Personal Financial Planning System",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to WiseLab API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
