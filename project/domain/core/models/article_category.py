from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped


from project.utils.base_model import Base
if TYPE_CHECKING:
    from project.domain.core.models.article import ArticleModel
    from project.domain.core.models.category import CategoryModel


class CategoryArticleModel(Base):
    __tablename__ = 'category_articles'

    article_id = Column(Integer,
                         ForeignKey('articles.id', onupdate='CASCADE', ondelete='CASCADE'),
                         primary_key=True)
    category_id = Column(Integer,
                         ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE'),
                         primary_key=True)

    article: Mapped["ArticleModel"] = relationship(back_populates="categories")
    category: Mapped["CategoryModel"] = relationship(back_populates="articles")