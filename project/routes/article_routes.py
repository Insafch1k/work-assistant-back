from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from project.BL.articles_bl import ArticleBL
from project.models.ArticleModel import CreateArticleModel, UpdateArticleModel

article_routes = Blueprint('article_routes', __name__)


@article_routes.route('/blog/create-article', methods=['POST'])
def create_article():
    try:
        data = CreateArticleModel(**request.get_json())
    except ValidationError as e:
        return jsonify({"message": "Ошибка валидации данных"}), 400

    answer, status_code = ArticleBL.create_article(data)

    return jsonify(answer), status_code


@article_routes.route('/blog/update_article', methods=['POST'])
def update_article():
    try:
        data = UpdateArticleModel(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': 'Ошибка валидации'})

    success = ArticleBL.update_article(data)

    if not success:
        return jsonify({'error': 'Статья не найдена'}), 400
    return jsonify(''), 204

@article_routes.route('/blog/articles/<slug>/<int:article_id>', methods=['GET'])
def read_article(slug, article_id):
    article = ArticleBL.get_article(article_id)

    if article is None:
        return jsonify({'error': 'Статья не обнаружена'}), 404

    return jsonify(article), 200

