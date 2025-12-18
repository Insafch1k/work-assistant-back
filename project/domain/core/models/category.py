from typing import List

from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import relationship, Mapped

from project.domain.core.models.article_category import CategoryArticleModel
from project.utils.base_model import Base


class Categoryodel(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, server_default=text("nextval('categories_id_seq'::regclass)"))
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)

    articles: Mapped[List["CategoryArticleModel"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    def __repr__(self):
        return f"<Category(id={self.id}, title='{self.title}', slug='{self.slug}')>"