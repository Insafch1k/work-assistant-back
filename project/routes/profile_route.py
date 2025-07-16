from project.utils.logger import Logger
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.profile_dal import ProfileDAL
from project.BL.profile_bl import form_response

profile_router = Blueprint("profile_router", __name__)
employer_profile_router = Blueprint("employer_profile_router", __name__)


@profile_router.route('/profile', methods=["PATCH"])
@jwt_required()
def update_profile():
    """Обновление профиля"""
    try:
        current_tg = get_jwt_identity()
        data = request.get_json()
        curr_id = ProfileDAL.get_user_id_by_tg(current_tg)

        role = ProfileDAL.get_user_role(curr_id)

        if role == "finder":
            ProfileDAL.update_profile(curr_id, user_name=data.get("user_name"), phone=data.get("phone"), photo=data.get("photo"))
            if "age" in data:
                ProfileDAL.update_finder_profile(data.get("age"), curr_id)
        if role == "employer":
            ProfileDAL.update_profile(curr_id, user_name=data.get("user_name"), phone=data.get("phone"), photo=data.get("photo"))
            if "organization_name" in data:
                ProfileDAL.update_employer_profile(data.get("organization_name"), curr_id)

        return jsonify({"message": "Профиль обновлён"}), 200
    except Exception as e:
        Logger.error(f"Error update profile {str(e)}")
        return jsonify({
            "message": f"Error update profile {str(e)}"
        }), 500


@profile_router.route('/profile/<int:profile_id>', methods=["GET"])
@jwt_required(optional=True)
def get_profile(profile_id):
    """Получение данных своего профиля"""
    try:
        current_tg = get_jwt_identity()
        curr_id = int(ProfileDAL.get_user_id_by_tg(current_tg))

        if curr_id and curr_id != profile_id:
            return jsonify({"message": "Нет доступа"}), 403

        data = ProfileDAL.get_profile_data(profile_id)
        if not data:
            return jsonify({"error": "Профиль не найден"}), 404

        response_data = form_response(data)
        return jsonify(response_data), 200
    except Exception as e:
        Logger.error(f"Error get profile {str(e)}")
        return jsonify({
            "message": f"Error get profile {str(e)}"
        }), 500


@employer_profile_router.route("/employers/<int:employer_id>", methods=["GET"])
@jwt_required(optional=True)
def get_employer_profile(employer_id):
    """Получение основной информации о работодателе"""
    try:
        profile = ProfileDAL.get_employer_profile_data(employer_id)
        if not profile:
            return jsonify({"error": "Работодатель не найден"}), 404

        jobs = ProfileDAL.get_employer_jobs(employer_id)

        jobs_json = []
        for job in jobs:
            jobs_json.append({
                "job_id": job[0],
                "title": job[1],
                "salary": job[2],
                "address": job[3],
            })
        return jsonify({
            "profile": {
                "user_name": profile[0],
                "rating": float(profile[1]),
                "tg_username": profile[2],
                "phone": profile[3],
                "photo": profile[4],
                "review_count": profile[5]
            },
            "vacancies": jobs_json
        }), 200
    except Exception as e:
        Logger.error(f"Error get employer profile {str(e)}")
        return jsonify({
            "message": f"Error get employer profile {str(e)}"
        }), 500


@employer_profile_router.route('/employers/<int:employer_id>/reviews', methods=["POST"])
@jwt_required()
def create_review(employer_id):
    """Создание отзыва о работодателе"""
    try:
        current_user_tg = get_jwt_identity()
        finder = ProfileDAL.check_finder(current_user_tg)
        if not finder:
            return jsonify({"error": "Только соискатели могут оставлять отзыв"}), 403

        user_id, finder_id = finder

        data = request.get_json()
        rating = data["rating"]
        comment = data["comment"]
        if not rating or not 1 <= rating <= 5:
            return jsonify({"error": "Оценка должна быть от 1 до 5"}), 400

        if not ProfileDAL.check_employer_exist(employer_id):
            return jsonify({"error": "Работодатель не найден"}), 404

        existing_review = ProfileDAL.check_review(employer_id, user_id)
        if existing_review:
            review_id = existing_review[0]
            review = ProfileDAL.update_review(rating, comment, review_id)

            action = "updated"
        else:
            review = ProfileDAL.add_review(employer_id, user_id, rating, comment)

            action = "created"

        ProfileDAL.update_rating(employer_id)

        return jsonify({
            "review_id": review[0],
            "rating": rating,
            "comment": comment,
            "created_at": review[1].isoformat(),
            "updated_at": review[2].isoformat(),
            "action": action
        }), 201 if action == "created" else 200
    except Exception as e:
        Logger.error(f"Error create review {str(e)}")
        return jsonify({
            "message": f"Error create review {str(e)}"
        }), 500
