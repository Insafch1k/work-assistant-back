from __future__ import annotations
from loguru import logger
from pydantic import BaseModel, ValidationError, constr

from project.utils.data_state import DataFailedMessage, DataState, DataSuccess

class ConfirmationValidateSchema(BaseModel):
    temporary_id: int
    code: int

    @classmethod
    def from_request(cls, json_data) -> DataState[ConfirmationValidateSchema]:
        try:
            return DataSuccess(ConfirmationValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при подтверждении почты: {errors}', error=e)

class RegistrationValidateSchema(BaseModel):
    username: str
    password: str
    email: str
    user_role: str

    @classmethod
    def from_request(cls, json_data) -> DataState[RegistrationValidateSchema]:
        try:
            return DataSuccess(RegistrationValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при регистрации: {errors}', error=e)

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
    def from_request(json_data) -> DataState[LoginTgValidateSchema]:
        try:
            return DataSuccess(LoginTgValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при входе в tg: {errors}',error=e)

class LoginValidateSchema(BaseModel):
    email: str
    password: str

    @staticmethod
    def from_request(json_data) -> DataState[LoginValidateSchema]:
        try:
            return DataSuccess(LoginValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при входе: {errors}',error=e)