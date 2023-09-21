from database.engine import engine, Session
from database.models import Base
import sqlalchemy

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
