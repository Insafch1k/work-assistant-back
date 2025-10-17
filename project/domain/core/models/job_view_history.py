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

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None
        }
        return data