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

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return data