from pydantic import BaseModel, ConfigDict


class Category(BaseModel):
    id: int
    title: str
    slug: str
    articles_count: int

    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    id: int
    title: str
    slug: str

    model_config = ConfigDict(from_attributes=True)