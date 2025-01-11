from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
# import os

# if os.path.exists("chat.db"):
#     os.remove("chat.db")

# Настройка подключения к базе данных
DATABASE_URL = "sqlite:///chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель чата
class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # Название чата
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted = Column(Boolean, default=False)  # Флаг для логического удаления чата

    # Связь с сообщениями
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

# Модель сообщения
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)  # 'user' или 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chat_id = Column(Integer, ForeignKey('chats.id'))

    # Связь с чатом
    chat = relationship("Chat", back_populates="messages")

# Создание таблиц
Base.metadata.create_all(bind=engine)

