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
    current_tg = get_jwt_identity()
    data = request.get_json()
    curr_id = ProfileDAL.get_user_id_by_tg(current_tg)

    if "user_id" in data and data["user_id"] != curr_id:
        return jsonify({"error": "Нет доступа"}), 403

    role = ProfileDAL.get_user_role(curr_id)

    #В ЗАВИСИМОСТИ ОТ ФРОНТА, НУЖНО БУДЕТ РАСПИСАТЬ ЭТИ ДАННЫЕ КАК НЕОБЯЗАТЕЛЬНЫЕ (КАК В filter_dal)
    if role == "finder":
        ProfileDAL.update_profile(data["user_name"], data["email"], data["phone"], data["photo"], curr_id)
        ProfileDAL.update_finder_profile(data["age"], curr_id)
    if role == "employer":
        ProfileDAL.update_profile(data["user_name"], data["email"], data["phone"], data["photo"], curr_id)
        ProfileDAL.update_employer_profile(data["organization_name"], curr_id)

    return jsonify({"message": "Профиль обновлён"}), 200


@profile_router.route('/profile/<int:profile_id>', methods=["GET"])
@jwt_required(optional=True)
def get_profile(profile_id):
    """Получение данных профиля"""
    current_tg = get_jwt_identity()
    curr_id = int(ProfileDAL.get_user_id_by_tg(current_tg))

    if curr_id and curr_id != profile_id:
        return jsonify({"message": "Нет доступа"}), 403

    data = ProfileDAL.get_profile_data(profile_id)
    if not data:
        return jsonify({"error": "Профиль не найден"}), 404

    response_data = form_response(data)
    return jsonify(response_data), 200


@employer_profile_router.route('/employers/<int:employer_id>', methods=["GET"])
@jwt_required(optional=True)
def get_employer_profile(employer_id):
    """Получение основной информации о работодателе"""
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
            "photo": profile[2],
            "review_count": profile[3]
        },
        "vacancies": jobs_json
    }), 200


@employer_profile_router.route('/employers/<int:employer_id>/reviews', methods=["POST"])
@jwt_required()
def create_review(employer_id):
    """Создание отзыва о работодателе"""
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
