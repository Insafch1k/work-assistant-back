from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from project.utils.base_model import Base
class JobsModel(Base):
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

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'city_id': self.city_id,
            'title': self.title,
            'wanted_job': self.wanted_job,
            'description': self.description,
            'salary': self.salary,
            'date': self.date.isoformat() if self.date else None,
            'time_start': self.time_start.isoformat() if self.time_start else None,
            'time_end': self.time_end.isoformat() if self.time_end else None,
            'address': self.address,
            'is_urgent': self.is_urgent,
            'status': self.status,
            'xp': self.xp,
            'age': self.age,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'car': self.car
        }
        return data