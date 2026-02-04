from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ValidationError
from project.utils.data_state import DataState, DataSuccess, DataFailedMessage


class CreateArticleValidateSchema(BaseModel):
    h1: str
    image_url: str
    description: str
    content: str
    seo_title: str
    category_ids: list[int]

    @classmethod
    def from_request(cls, json_data) -> DataState[CreateArticleValidateSchema]:
        try:
            return DataSuccess(CreateArticleValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка при создании статьи: {errors}', error=e)

class CreateCategoryValidateSchema(BaseModel):
    title: str

    @classmethod
    def from_request(cls, json_data) -> DataState[CreateCategoryValidateSchema]:
        try:
            return DataSuccess(CreateCategoryValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка при создании категории: {errors}', error=e)
