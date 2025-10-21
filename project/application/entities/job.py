from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Job(BaseModel):
    id: Optional[int] = None
    user_id: int
    city_id: int
    title: str
    wanted_job: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[int] = None
    date: Optional[datetime] = None
    time_start: Optional[time] = None
    time_end: Optional[time] = None
    address: Optional[str] = None
    is_urgent: bool = False
    status: bool = True
    xp: Optional[str] = None
    age: Optional[str] = None
    created_at: Optional[datetime] = None
    car: bool = False

    model_config = ConfigDict(from_attributes=True)

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