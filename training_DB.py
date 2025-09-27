from sqlalchemy import Integer, Column, create_engine, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base

engine = create_engine('sqlite:///my_db.db', echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()