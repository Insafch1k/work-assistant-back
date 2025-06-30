from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.favorite_dal import FavoriteDAL

favorite_router = Blueprint("favorite_router", __name__)


@favorite_router.route("/jobs/<int:job_id>/add_favorite", methods=["POST"])
@jwt_required()
def add_favorite(job_id):
    """Добавление вакансии в избранное"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    if not FavoriteDAL.check_job(job_id):
        return jsonify({"error": "Работа не найдена"}), 404

    data = request.get_json()
    favorite_by = FavoriteDAL.get_status_job(curr_id, data["job_id"])

    return jsonify({
        "favorite_id": favorite_by[0],
        "finder_id": favorite_by[1],
        "job_id": favorite_by[2],
        "created_at": favorite_by[3],
    }), 200


@favorite_router.route("/jobs/remove_favorite/<int:favorite_id>", methods=["DELETE"])
@jwt_required()
def remove_favorite(favorite_id):
    """Удаление вакансии из избранного"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    favorite = FavoriteDAL.delete_favorite_job(current_user_tg, favorite_id)
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

    favorites = FavoriteDAL.get_favorite_list(current_user_tg)

    favorite_json = []
    for fav in favorites:
        favorite_json.append({
            "favorite_id": fav[8],
            "job_id": fav[0],
            "title": fav[1],
            "salary": fav[2],
            "address": fav[3],
            "date": fav[4].isoformat() if fav[4] else None,
            "time_start": fav[5].isoformat() if fav[5] else None,
            "time_end": fav[6].isoformat() if fav[6] else None,
            "organization": fav[7]
        })

    return jsonify(favorites), 200