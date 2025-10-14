from __future__ import annotations
from loguru import logger
from pydantic import BaseModel, ValidationError

from project.utils.data_state import DataFailedMessage, DataState, DataSuccess


class RegisterTgValidateSchema(BaseModel):
    tg_id: int
    tg_username: str
    user_name: str
    user_role: str

    @staticmethod
    def from_request(json_data) -> DataState[RegisterTgValidateSchema]:
        try:
            return DataSuccess(RegisterTgValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при регистрации в tg: {errors}',error=e)

class LoginTgValidateSchema(BaseModel):
    tg_id: int
    tg_username: str

    @staticmethod
    def from_request(json_data) ->  DataState[LoginTgValidateSchema]:
        try:
            return DataSuccess(LoginTgValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при входе в tg: {errors}',error=e)