from project.utils.vars.enums import CategoryEnum


class CreateArticleModel(BaseModel):
    title: str
    author: int
    header: Optional[str]
    description: Optional[str]
    category: CategoryEnum

class UpdateArticleModel(BaseModel):
    """Модель по сути проверяет наличие только 1 поля - id статьи,
    необходимо в BLL сделать вызов функции, которая бы проверяла, что помимо
    id есть хотя бы 1 поле, которое требуется обновить"""
    id: int
    author: Optional[int]
    header: Optiona[str]
    description: Optional[str]
    category: Optional[CategoryEnum]


