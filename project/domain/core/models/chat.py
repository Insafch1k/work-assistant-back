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

class ChatModel(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    finder_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", onupdate="CASCADE", ondelete="CASCADE"))

    # в БД default '-1'::integer
    last_message_finder_id = Column(
        Integer,
        nullable=False,
        server_default=text("-1"),
        default=-1,
    )
    last_message_employer_id = Column(
        Integer,
        nullable=False,
        server_default=text("-1"),
        default=-1,
    )

    name = Column(String, nullable=False)

    # связи (предполагаем, что UserModel уже объявлен)
    finder = relationship("UserModel", foreign_keys=[finder_id])
    employer = relationship("UserModel", foreign_keys=[employer_id])

    messages = relationship(
        "MessageModel",
        back_populates="chat",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

