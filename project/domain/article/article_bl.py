from typing import Optional
from project.application.entities.user import User
from project.application.routes.articles.article_schemas import CreateArticleValidateSchema, \
    CreateCategoryValidateSchema
from project.domain.admin.admin_dal import AdminDal
from project.domain.article.article_dal import ArticleDal
from project.domain.authorization.auth_bl import AuthBl
from project.utils.data_state import DataState


class ArticleBl:
    @staticmethod
    def get_articles(limit, offset, category_id, sort,search):
        return ArticleDal.get_articles(limit, offset, category_id, sort,search)

    @staticmethod
    def get_categories():
        return ArticleDal.get_categories()

    @staticmethod
    def get_article_info(slug):
        return ArticleDal.get_article_info(slug)

    @staticmethod
    def create_article(result: CreateArticleValidateSchema):
        return ArticleDal.create_article(result.h1,result.image_url,result.description,result.content,result.category_ids)

    @staticmethod
    def create_category(result: CreateCategoryValidateSchema):
        return ArticleDal.create_category(result.title)