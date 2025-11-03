from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from project.utils.base_model import Base

class JobViewHistoryModel(Base):
    __tablename__ = 'job_view_history'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, server_default="nextval('job_view_history_id_seq'::regclass)")
    user_id = Column(Integer, ForeignKey('public.users.id', ondelete='CASCADE'))
    job_id = Column(Integer, ForeignKey('public.jobs.id', ondelete='CASCADE'))
    viewed_at = Column(DateTime, default=func.now())

    job = relationship("JobModel", back_populates="histories")

