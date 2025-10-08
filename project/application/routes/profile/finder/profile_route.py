from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger

from project.domain.profile.employer.profile_bl import EmployerProfileBl

employer_profile_router = Blueprint("employer_profile_router", __name__)
@employer_profile_router.route('/profile/me', methods=["GET"])
@jwt_required()
def get_profile_1():
    """Получение данных своего профиля"""
    user_id = get_jwt_identity()
    data_state = EmployerProfileBl.get_profile_1(user_id=user_id)
    if not data_state:
        return jsonify({"error": data_state.error_message}), 404

    return jsonify(data_state.data), 200

def get_profile_2():
    """Получение данных своего профиля"""
    user_id = get_jwt_identity()
    try:
        data = EmployerProfileBl.get_profile_2(user_id=user_id)
        return jsonify(data), 200 # или можно просто return data ???
    except Exception as ex:
        logger.error(ex)
        return jsonify({"error": ex}), 404
