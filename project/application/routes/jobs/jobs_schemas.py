from __future__ import annotations

from datetime import time, datetime
from typing import Optional

from loguru import logger
from pydantic import BaseModel, ValidationError, Field

from project.utils.data_state import DataFailedMessage, DataState, DataSuccess


class CreateNewJobValidateSchema(BaseModel):
    title: Optional[str]
    wanted_job: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[int] = None
    date: Optional[datetime] = None
    time_start: Optional[time] = None
    time_end: Optional[time] = None
    address: Optional[str] = None
    city_id: Optional[int]
    xp: Optional[int]
    age: Optional[int]
    is_urgent: Optional[bool]
    car: Optional[bool]

    @classmethod
    def from_request(cls, json_data) -> DataState[CreateNewJobValidateSchema]:
        try:
            return DataSuccess(CreateNewJobValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при создании работы: {errors}',error=e)

class GetJobsValidateSchema(BaseModel):
    search: Optional[str] = None
    employer_id: Optional[int] = None
    time_start: Optional[time] = None
    time_end: Optional[time] = None
    car: Optional[bool] = None
    is_urgent: Optional[bool] = None
    salary: Optional[int] = Field(default_factory=lambda: None, ge=0)
    age: Optional[int] = Field(default_factory=lambda: None,gt=0)
    xp: Optional[int] = Field(default_factory=lambda: None,ge=0)
    date: Optional[datetime] = None
    city_id: Optional[int] = None
    address: Optional[str] = None
    wanted_job: Optional[str] = None

    @classmethod
    def from_request(cls, json_data) -> DataState[GetJobsValidateSchema]:
        try:
            return DataSuccess(GetJobsValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при получении работ: {errors}',error=e)

class UpdateJobSchema(BaseModel):

    job: Optional[CreateNewJobValidateSchema] = None

    @staticmethod
    def from_request(json_data: dict) -> DataState:
        try:
            data = CreateNewJobValidateSchema(**json_data)
            return DataSuccess(UpdateJobSchema(job=data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0], "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации вакансии: {errors}',error=e)

    def get_update_fields(self) -> dict:
        """Возвращает только переданные поля для обновления"""
        update_data = {}

        if self.job is not None:
            # Используем встроенные возможности Pydantic
            job_data = self.job.model_dump(
                exclude_none=True,  # исключаем None
                exclude_unset=True  # исключаем непереданные поля
            )

            if job_data:
                update_data['job'] = job_data

        return update_data

