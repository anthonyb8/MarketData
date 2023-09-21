from sqlalchemy import create_engine, exc
import sqlalchemy.orm as orm 
import os
from dotenv import load_dotenv

load_dotenv()

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
except exc.ArgumentError as e:
    raise ValueError("Invalid DATABASE_URL") from e

Session = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

