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
    id: int
    author: int = Field(None)
    header: str = Field(None)
    description: str = Field(None)
    category: CategoryEnum = Field(None)

class DeleteArticleModel(BaseModel):
    id: int

class ReadArticleModel(BaseModel):
    id: int


