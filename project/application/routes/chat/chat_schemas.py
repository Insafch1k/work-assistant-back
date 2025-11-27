from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ValidationError, Field
from project.utils.data_state import DataState, DataSuccess, DataFailedMessage


class CreateChatValidateSchema(BaseModel):
    penpal_id: int
    job_id: int

    @classmethod
    def from_request(cls, json_data) -> DataState[CreateChatValidateSchema]:
        try:
            return DataSuccess(CreateChatValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при создании чата: {errors}', error=e)

class SendMessageValidateSchema(BaseModel):
    text: str = Field(min_length=1)

    @classmethod
    def from_request(cls, json_data) -> DataState[SendMessageValidateSchema]:
        try:
            return DataSuccess(SendMessageValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при отправке сообщения в чат: {errors}', error=e)
