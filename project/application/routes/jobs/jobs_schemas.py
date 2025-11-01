from __future__ import annotations

from typing import Optional

from loguru import logger
from pydantic import BaseModel, ValidationError

from project.utils.data_state import DataFailedMessage, DataState, DataSuccess


class CreateNewJobValidateSchema(BaseModel):
    title: Optional[str] = None
    wanted_job: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[int] = None
    date: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    xp: Optional[str] = None
    age: Optional[str] = None
    is_urgent: Optional[bool] = None
    car: Optional[bool] = None

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

class UpdateJobSchema(BaseModel):

    job: Optional[CreateNewJobValidateSchema] = None

    @staticmethod
    def from_request(json_data: dict) -> DataState[UpdateJobSchema]:
        try:
            # Обрабатываем вложенный объект resume
            if 'job' in json_data and isinstance(json_data['job'], dict):
                json_data['job'] = UpdateJobSchema(**json_data['job'])
            return DataSuccess(UpdateJobSchema(**json_data))
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

