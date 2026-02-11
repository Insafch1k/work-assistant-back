from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, text, DateTime, func
from sqlalchemy.orm import relationship, Mapped
from project.utils.base_model import Base
if TYPE_CHECKING:
    from project.domain.core.models.article_category import CategoryArticleModel


class ArticleModel(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, server_default=text("nextval('articles_id_seq'::regclass)"))
    h1 = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    seo_title = Column(String, nullable=False)
    image_url = Column(String)
    description = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),  # в SQL у тебя NOT NULL, без default – можно задать на уровне ORM
        default=func.now(),
    )

    # строковые ссылки избегают раннего импорта зависимых моделей
    categories: Mapped[List["CategoryArticleModel"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


    def __repr__(self):
        return f"<Article(id={self.id}, h1='{self.h1}', slug='{self.slug}')>"