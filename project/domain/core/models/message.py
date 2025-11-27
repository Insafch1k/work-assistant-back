from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    text,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),  # в SQL у тебя NOT NULL, без default – можно задать на уровне ORM
        default=func.now(),
    )

    chat = relationship("ChatModel", back_populates="messages")
    sender = relationship("UserModel")