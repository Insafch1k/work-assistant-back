from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.favorite_dal import FavoriteDAL

favorite_router = Blueprint("favorite_router", __name__)


@favorite_router.route('/jobs/<int:job_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite(job_id):
    """Добавление/удаление вакансии в избранное"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    if not FavoriteDAL.check_job(job_id):
        return jsonify({"error": "Работа не найдена"}), 404

    favorite_by = FavoriteDAL.get_status_job(job_id) or []

    if curr_id in favorite_by:
        favorite_by.remove(curr_id)
        action = "removed"
    else:
        favorite_by.append(curr_id)
        action = "added"

    updated_job = FavoriteDAL.update_favorite_status(favorite_by, job_id)

    return jsonify({
        "job_id": updated_job[0],
        "title": updated_job[1],
        "is_favorite": curr_id in (updated_job[2] or []),
        "action": action
    }), 200


@favorite_router.route('/jobs/favorites', methods=['GET'])
@jwt_required()
def get_favorite_jobs():
    """Получение избранных вакансий"""
    current_user_tg = get_jwt_identity()
    curr_id = FavoriteDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    favorites = []
    abed = FavoriteDAL.get_favorite_list(curr_id)
    print(abed)
    for job in abed:
        favorites.append({
            "job_id": job[0],
            "title": job[1],
            "salary": job[2],
            "address": job[3],
            "time_start": job[4].isoformat() if job[4] else None,
            "time_end": job[5].isoformat() if job[5] else None,
            "is_favorite": True
        })

    return jsonify(favorites), 200