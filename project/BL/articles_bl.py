import datetime
from sqlite3 import DataError, DatabaseError

from flask import jsonify
from pydantic import ValidationError
from werkzeug.exceptions import ServiceUnavailable

from project.models.ArticleModel import CreateArticleModel, UpdateArticleModel
from ..DAL.articles_dal import ArticlesDAL
from ..utils.logger import Logger
from ..utils.universal.universal_var import transform_to_slug
from ..utils.vars.status_code import HttpStatusCode

class ArticleBL:

    @staticmethod
    def get_article(article_id):
        article_data = ArticlesDAL.read_article(article_id)
        return article_data

    @staticmethod
    def create_article(model: CreateArticleModel):
        model.slug = transform_to_slug(model.header)

        try:
            result = ArticlesDAL.create_article(model) # -> boolean

            if result:
                ret = {
                    "status": "success",
                    "message": f"Статья {model.header} успешно создана"}
                status_code = HttpStatusCode.CREATED
            else:
                ret = {
                    "status": "error",
                    "message": "Не получилось создать статью"
                }

                status_code = HttpStatusCode.BAD_REQUEST

            return ret, status_code

        except Exception as e:
            Logger.error(f"Error creating article {str(e)}")
            return {"status": "error", "message": "Внутренняя  ошибка серверм"}, HttpStatusCode.INTERNAL_SERVER_ERROR

    @staticmethod
    def update_article(model) -> bool:

        try:
            updated_count = ArticlesDAL().update_article(model)
        except DatabaseError as e:
            raise ServiceUnavailable("DB temporarily unavailable") from e

        result = True if updated_count is not None else False

        return result

    @staticmethod
    def get_all_articles(category=None):
        result = ArticlesDAL.get_all_articles(category)

        if not result:
            return False, None
        else:
            rows = [dict(r) for r in result]
            print(f"До: {rows}")

            for row in rows:
                if isinstance(row.get("created_at"), (datetime.date, datetime.datetime)):
                    row["created_at"] = row["created_at"].isoformat()
                if isinstance(row.get("updated_at"), (datetime.date, datetime.datetime)):
                    row["updated_at"] = row["updated_at"].isoformat()

            print(f"После: {rows}")
            print(type(rows[0]["created_at"]))  # должно вывести <class 'str'>
            return True, rows

