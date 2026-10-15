from fastapi import FastAPI # type: ignore
from app.api.routes.v1 import auth, users
from app.db.database import engine, Base

# Import all models so SQLAlchemy knows about them before creating tables
from app.models import user, session

# Create database tables automatically (for development)
# In production, you would use Alembic migrations instead
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application instance
app = FastAPI(
    title="Login API",
    description="A modular Login API using FastAPI",
    version="1.0.0"
)

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is up and running"}
