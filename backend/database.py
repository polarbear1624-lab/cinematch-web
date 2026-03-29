from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This creates a file named cinephile.db in your folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./cinephile.db"

# The engine is what actually talks to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A session is a temporary workspace for our database queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the base class for our database models
Base = declarative_base()