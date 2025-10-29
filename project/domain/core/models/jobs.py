from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from project.utils.base_model import Base
class JobModel(Base):
    __tablename__ = 'jobs'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, server_default="nextval('jobs_id_seq'::regclass)")
    user_id = Column(Integer, ForeignKey('public.users.id', ondelete='CASCADE'))
    city_id = Column(Integer, ForeignKey('public.cities.id', ondelete='RESTRICT'))
    title = Column(Text, nullable=False)
    wanted_job = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    salary = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=True)
    time_start = Column(DateTime, nullable=True)
    time_end = Column(DateTime, nullable=True)
    address = Column(Text, nullable=True)
    is_urgent = Column(Boolean, default=False)
    status = Column(Boolean, default=True)
    xp = Column(Text, nullable=True)
    age = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    car = Column(Boolean, default=False)

