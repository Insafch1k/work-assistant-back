from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.profile_dal import ProfileDAL
from project.BL.profile_bl import form_response

profile_router = Blueprint("profile_router", __name__)


@profile_router.route('/profile', methods=["POST", "PUT"])
@jwt_required()
def update_profile():
    current_tg = get_jwt_identity()
    data = request.get_json()
    curr_id = int(ProfileDAL.get_user_id_by_tg(current_tg))

    if "user_id" in data and data["user_id"] != curr_id:
        return jsonify({"error": "Forbidden"}), 403

    role = ProfileDAL.get_user_role(curr_id)

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
    current_tg = get_jwt_identity()
    curr_id = int(ProfileDAL.get_user_id_by_tg(current_tg))

    if curr_id and curr_id != profile_id:
        return jsonify({"message": "Нет доступа"}), 403

    data = ProfileDAL.get_profile_data(profile_id)
    if not data:
        return jsonify({"error": "Профиль не найден"}), 404

    response_data = form_response(data)
    #response = ProfileResponse(**response_data)
    return jsonify(response_data), 200