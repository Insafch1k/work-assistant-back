from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Integer

from project.utils.base_model import Base


class EventModel(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)