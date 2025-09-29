from typing import Optional

from pydantic import BaseModel, Field

from project.utils.vars.enums import CategoryEnum


class CreateArticleModel(BaseModel):
    author: int = Field(None)
    header: str = Field(None)
    description: str = Field(None)
    category: CategoryEnum
    slug: str= Field(None)

class UpdateArticleModel(BaseModel):
    """Модель по сути проверяет наличие только 1 поля - id статьи,
    необходимо в BLL сделать вызов функции, которая бы проверяла, что помимо
    id есть хотя бы 1 поле, которое требуется обновить"""
    id: int
    author: Optional[int]
    header: Optional[str]
    description: Optional[str]
    category: Optional[CategoryEnum]

class DeleteArticleModel(BaseModel):
    id: int


class ReadArticleModel(BaseModel):
    id: int


