from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime




engine = create_engine('sqlite:///my_db.db', echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    # relationships
    chats = relationship('Chat', back_populates='owner')


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(15), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    # relationships
    messages = relationship('Message', back_populates='chat')
    owner = relationship('User', back_populates='chats')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    content = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chat_id = Column(ForeignKey('chats.id'))
    #relationships
    chat = relationship('Chat', back_populates='messages')

# Создаем таблицы после определения всех моделей
Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()