from app.db.database import SessionLocal

def get_db():
    """
    Dependency function that yields a database session for a single request
    and securely closes it when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

