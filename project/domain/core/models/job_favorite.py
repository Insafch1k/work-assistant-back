from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from project.utils.base_model import Base
class JobFavoriteModel(Base):
    __tablename__ = 'job_favorites'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, server_default="nextval('job_favorites_id_seq'::regclass)")
    user_id = Column(Integer, ForeignKey('public.users.id', ondelete='CASCADE'))
    job_id = Column(Integer, ForeignKey('public.jobs.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=func.now())

