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
from project.domain.core.models.jobs import JobModel


class ChatModel(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    finder_id = Column(Integer, ForeignKey(UserModel.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    employer_id = Column(Integer, ForeignKey(UserModel.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey(JobModel.id, onupdate="CASCADE", ondelete="CASCADE"))

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


