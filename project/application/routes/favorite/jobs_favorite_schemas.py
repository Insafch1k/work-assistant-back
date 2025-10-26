from __future__ import annotations
from loguru import logger
from pydantic import BaseModel, ValidationError

from project.utils.data_state import DataFailedMessage, DataState, DataSuccess


class AddJobToFavoriteValidateSchema(BaseModel):
    job_id: int

    @classmethod
    def from_request(cls, json_data) -> DataState[AddJobToFavoriteValidateSchema]:
        try:
            return DataSuccess(AddJobToFavoriteValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при добавлении работы в избранное: {errors}',error=e)
