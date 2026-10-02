from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, students, schools, programs, applications, favorites, submissions, recommendations
from app.db.database import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ApplyCM API",
    description="Backend API for ApplyCM school search and unified application platform",
    version="1.0.0"
)

# CORS middleware configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including API routers under /api namespace
app.include_router(auth.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(schools.router, prefix="/api")
app.include_router(programs.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the ApplyCM API"}