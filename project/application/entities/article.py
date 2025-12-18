from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from project.application.entities.category import Category, CategoryBase


class Article(BaseModel):
    h1: str
    slug: str
    image_url: str
    description: str
    content: str
    categories: list[CategoryBase]
    created_at: datetime  # или datetime если преобразуете


    @field_validator('categories', mode='before')
    @classmethod
    def extract_categories_from_associations(cls, categories):
        return [CategoryBase.model_validate(data.category) for data in categories]

    model_config = ConfigDict(from_attributes=True)


class ArticleBaseInfo(BaseModel):
    h1: str
    slug: str
    image_url: str
    description: str
    categories: list[CategoryBase]
    created_at: datetime  # или datetime если преобразуете

    @field_validator('categories', mode='before')
    @classmethod
    def extract_categories_from_associations(cls, categories):
        return [CategoryBase.model_validate(data.category) for data in categories]

    model_config = ConfigDict(from_attributes=True)