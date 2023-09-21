from database.engine import engine, Session
from database.models import Base
import sqlalchemy
from sqlalchemy import text
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.orm import Session as session

def _get_db():
    db = None
    try:
        db = Session()
        yield db
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise RuntimeError("Error with database session") from e
    finally:
        if db:
            db.close()

def _check_database_connection(db: "session"):
    """Checks if the API can successfully connect to the database."""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {"status": "success", "message": "Successfully connected to the database"}
    except Exception as e:
        return {"status": "failure", "message": f"Database connection failed: {e}"}

def _create_tables():
    try:
        return Base.metadata.create_all(bind=engine)
    except sqlalchemy.exc.OperationalError as e:
        if "some specific string in the error message" in str(e):
            raise ValueError("Invalid URL format: 'postgresql://user:password@host/databaseName'")
        raise RuntimeError(f"Database operational error: {e}")

def _delete_tables():
    try:
        Base.metadata.drop_all(bind=engine)
    except sqlalchemy.exc.OperationalError as e:
        if "some specific string in the error message" in str(e):
            raise ValueError("Invalid URL format: 'postgresql://user:password@host/databaseName'")
        raise RuntimeError(f"Database operational error: {e}")
