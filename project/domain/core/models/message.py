from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    text,
)
from project.utils.base_model import Base
from project.domain.core.models.user import UserModel
from project.domain.core.models.chat import ChatModel


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey(ChatModel.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey(UserModel.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),  # в SQL у тебя NOT NULL, без default – можно задать на уровне ORM
        default=func.now(),
    )
