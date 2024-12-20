from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

SQL_DATABASE_URL = "postgresql://postgres:9207400638@localhost:5432/blog_management"

engine =  create_engine(SQL_DATABASE_URL)

sessionLocal = sessionmaker(autocommit=True,autoflush=True,engine=engine)

Base = declarative_base()

def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()
