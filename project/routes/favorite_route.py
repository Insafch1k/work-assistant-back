from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime

from project.BL.job_bl import time_calculate
from project.DAL.favorite_dal import FavoriteDAL

favorite_router = Blueprint("favorite_router", __name__)


@favorite_router.route("/jobs/<int:job_id>/add_favorite", methods=["POST"])
@jwt_required()
def add_favorite(job_id):
    """Добавление вакансии в избранное"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    print("CURR_ID", curr_id, "\n\n")
    print("JOB ID", job_id, "\n\n")
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    # if not FavoriteDAL.check_job(job_id):
    #     return jsonify({"error": "Работа не найдена"}), 404

    # data = request.get_json()

    favorite = FavoriteDAL.add_job_favorite(curr_id, job_id)
    print("ПОЛУЧЕННЫЕ ДАННЫЕ", favorite, "\n\n\n")
    if not favorite:
        return jsonify({"error": "Вакансия уже в списке избранных"}), 401
    else:
        return jsonify({
            "favorite_id": favorite[0],
            "finder_id": favorite[1],
            "job_id": favorite[2],
            "created_at": favorite[3],
        }), 200


@favorite_router.route("/jobs/<int:job_id>/remove_favorite", methods=["DELETE"])
@jwt_required()
def remove_favorite(job_id):
    """Удаление вакансии из избранного"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    favorite = FavoriteDAL.delete_favorite_job(curr_id, job_id)
    if not favorite:
        return jsonify({"error": "Работа не найдена"}), 404

    return jsonify({"message": "Удалено из избранного"}), 200


@favorite_router.route("/jobs/get_favorite", methods=["GET"])
@jwt_required()
def get_favorites():
    """Получение списка избранных вакансий"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    favorite = FavoriteDAL.get_favorite_list(curr_id)
    if not favorite:
        return jsonify({"error": "Избранные не найдены"}), 404

    favorite_json = []
    for fav in favorite:
        hours = time_calculate(fav[4], fav[5])
        favorite_json.append({
            "favorite_id": fav[0],
            "job_id": fav[1],
            "title": fav[2].strip() if isinstance(fav[2], str) else fav[2],
            "salary": fav[3],
            "hours": hours,
            "address": fav[6].strip() if isinstance(fav[6], str) else fav[6],
            "rating": fav[7],
            "photo": fav[8],
            "is_favorite": fav[9]
        })

    return jsonify(favorite_json), 200
