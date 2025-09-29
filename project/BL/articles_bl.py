from project.models.ArticleModel import CreateArticleModel
from ..DAL.articles_dal import ArticlesDAL
from ..utils.logger import Logger
from ..utils.universal.universal_var import transform_to_slug
from ..utils.vars.status_code import HttpStatusCode

class ArticleBL:
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
