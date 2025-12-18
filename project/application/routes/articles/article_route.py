from flask import Blueprint, request
from project.application.routes.articles.article_schemas import CreateArticleValidateSchema, \
    CreateCategoryValidateSchema
from project.domain.article.article_bl import ArticleBl
from project.utils.data_state import  DataFailedMessage
from project.utils.is_admin import admin_required

article_router = Blueprint("article_router", __name__)


@article_router.route('/articles', methods=["GET"])
def get_articles():
    try:
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
        category_id = request.args.get("category_id")
        search = request.args.get("search")
        sort = int(request.args.get("sort", 0))

        return ArticleBl.get_articles(limit,offset,category_id,sort, search).to_response()
    except Exception as e:
        return DataFailedMessage("Ошибка при получении списка статей", error=e).to_response()

@article_router.route('/categories', methods=['GET'])
def get_categories():
    try:
        return ArticleBl.get_categories().to_response()

    except Exception as e:
        return DataFailedMessage("Ошибка при получении списка категорий", error=e).to_response()

@article_router.route('/articles/<string:slug>', methods=['GET'])
def get_article_info(slug):
    try:
        return ArticleBl.get_article_info(slug).to_response()
    except Exception as e:
        return DataFailedMessage("Ошибка при получении статьи", error=e).to_response()

@article_router.route('/articles', methods=['POST'])
#@admin_required()
def create_article():
    try:
        json_data = request.get_json()
        validate_data_state = CreateArticleValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()
        return ArticleBl.create_article(validate_data_state.data).to_response()
    except Exception as e:
        return DataFailedMessage("Ошибка при создании статьи", error=e).to_response()

@article_router.route('/categories', methods=['POST'])
#@admin_required()
def create_category():
    try:
        json_data = request.get_json()
        validate_data_state = CreateCategoryValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()
        return ArticleBl.create_category(validate_data_state.data).to_response()
    except Exception as e:
        return DataFailedMessage("Ошибка при создании категории", error=e).to_response()