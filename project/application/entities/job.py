from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from project.application.entities.user import UserBaseInfo


class Job(BaseModel):
    id: Optional[int] = None
    user_id: int
    city_id: int
    city: Optional[str] = None
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
    xp: Optional[int] = None
    age: Optional[int] = None
    created_at: Optional[datetime] = None
    car: bool = False
    is_favorite: Optional[bool] = False


    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'city_id': self.city_id,
            'city': self.city,
            'title': self.title,
            'wanted_job': self.wanted_job,
            'description': self.description,
            'salary': self.salary,
            'date': self.date.strftime("%d-%m-%Y") if self.date else None,
            'time_start': self.time_start.isoformat() if self.time_start else None,
            'time_end': self.time_end.isoformat() if self.time_end else None,
            'address': self.address,
            'is_urgent': self.is_urgent,
            'status': self.status,
            'xp': self.xp,
            'age': self.age,
            'created_at': self.created_at.strftime("%d-%m-%Y %H:%M:%S") if self.created_at else None,
            'car': self.car,
            'is_favorite': self.is_favorite
        }
        return data

class JobBaseInfo(BaseModel):
    id: Optional[int] = None
    user: UserBaseInfo
    title: str
    city: str
    salary: Optional[int] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    address: Optional[str] = None
    is_urgent: bool = False
    car: bool = False
    is_favorite: Optional[bool] = False

    @field_validator('user', mode='before')
    @classmethod
    def extract_user(cls, user):
        return UserBaseInfo.model_validate(user)

    @field_validator('time_start', mode='before')
    @classmethod
    def extract_time_start(cls, time_start):
        return time_start.isoformat()

    @field_validator('time_end', mode='before')
    @classmethod
    def extract_time_end(cls, time_end):
        return time_end.isoformat()

    model_config = ConfigDict(from_attributes=True)

class JobInfo(BaseModel):
    id: Optional[int] = None
    user: UserBaseInfo
    city: Optional[str] = None
    title: str
    wanted_job: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[int] = None
    date: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    address: Optional[str] = None
    is_urgent: bool = False
    status: bool = True
    xp: Optional[int] = None
    age: Optional[int] = None
    created_at: Optional[datetime] = None
    car: bool = False
    is_favorite: Optional[bool] = False

    @field_validator('user', mode='before')
    @classmethod
    def extract_user(cls, user):
        return UserBaseInfo.model_validate(user)

    @field_validator('time_start', mode='before')
    @classmethod
    def extract_time_start(cls, time_start):
        return time_start.isoformat()

    @field_validator('time_end', mode='before')
    @classmethod
    def extract_ztime_end(cls, time_end):
        return time_end.isoformat()

    @field_validator('date', mode='before')
    @classmethod
    def extract_time_end(cls, date):
        return date.strftime("%d-%m-%Y")

    model_config = ConfigDict(from_attributes=True)
