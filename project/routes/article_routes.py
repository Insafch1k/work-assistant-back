from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from project.BL.articles_bl import ArticleBL
from project.models.ArticleModel import CreateArticleModel

article_routes = Blueprint('article_routes', __name__)

@article_routes.route('/blog/create-article', methods=['POST'])
def create_articles():

    try:
        data = CreateArticleModel(**request.get_json())
    except ValidationError as e:
        return jsonify({"message": "Ошибка валидации данных"}), 400

    answer, status_code = ArticleBL.create_article(data)

    return jsonify(answer), status_code



