from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ValidationError
from project.utils.data_state import DataState, DataSuccess, DataFailedMessage


class GetUsersValidateSchema(BaseModel):
    limit: int
    offset: int
    name_filter: Optional[str] = None

    @classmethod
    def from_request(cls, json_data) -> DataState[GetUsersValidateSchema]:
        try:
            return DataSuccess(GetUsersValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при подтверждении почты: {errors}', error=e)

class BanUserValidateSchema(BaseModel):
    user_id: int

    @classmethod
    def from_request(cls, json_data) -> DataState[BanUserValidateSchema]:
        try:
            return DataSuccess(BanUserValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при подтверждении почты: {errors}', error=e)