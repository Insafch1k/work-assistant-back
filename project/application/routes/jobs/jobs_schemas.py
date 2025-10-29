from __future__ import annotations
from loguru import logger
from pydantic import BaseModel, ValidationError

from project.utils.data_state import DataFailedMessage, DataState, DataSuccess


class CreateNewJobValidateSchema(BaseModel):
    title: str
    wanted_job: str
    description: str
    salary: int
    date: str
    time_start: str
    time_end: str
    address: str
    city: str
    xp: str
    age: str
    is_urgent: bool
    car: bool

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

