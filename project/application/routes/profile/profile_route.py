from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from project.application.routes.profile.profile_schemas import UpdateProfileSchema
from project.domain.profile.employer.profile_bl import EmployerProfileBl
from project.domain.profile.finder.profile_bl import FinderProfileBl
from project.domain.profile.get_role import get_user_role
from project.utils.data_state import DataFailedMessage

profile_router = Blueprint("profile_router", __name__)

def get_profile_bl(user_id: str):
    """Фоабрика для получения сответствующего BL класса"""
    user_role = get_user_role(user_id)
    bl_map = {
        'finder': FinderProfileBl,
        'employer': EmployerProfileBl
    }
    return bl_map.get(user_role)

@profile_router.route('/profile/me', methods=["GET"])
@jwt_required()
def get_profile():
    """Получение данных своего профиля"""
    try:
        user_id = get_jwt_identity()
        data_state = get_profile_bl(user_id).get_profile(user_id=user_id)

        if not data_state:
            return data_state.to_response()

        return jsonify(data_state.data), 200

    except Exception as e:
        return DataFailedMessage(f"Не удалось получить профиль",error=e).to_response()

@profile_router.route('/profile/change_role', methods=["GET"])
@jwt_required()
def change_role():
    """Обновление роли"""
    try:
        user_id = get_jwt_identity()
        data_state = get_profile_bl(user_id).change_role(user_id=user_id)
        if not data_state:
            return data_state.to_response()

        return jsonify(data_state.data), 200

    except Exception as e:
        return DataFailedMessage(f"Не удалось сменить роль",error=e).to_response()

@profile_router.route('/profile', methods=["PATCH"])
@jwt_required()
def update_profile():
    """Обновление профиля
    :param - можно передать любые поля:
    {user_name, phone, photo, resume:{job_title, education, work_xp, skills}}
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if len(data) == 0:
            return jsonify({"error": "No fields to update"}), 400

        data_state = UpdateProfileSchema.from_request(data)
        if not data_state:
            return data_state.to_response()

        update_data = data_state.data.get_update_fields()
        data_state = get_profile_bl(user_id).update_profile(user_id=user_id, updated_data=update_data)
        if not data_state:
            return data_state.to_response()

        return jsonify(data_state.data), 200

    except Exception as e:
        return DataFailedMessage(f"Не удалось обновить профиль", error=e).to_response()


# def get_profile_2():
#     """Получение данных своего профиля"""
#     user_id = get_jwt_identity()
#     try:
#         data = EmployerProfileBl.get_profile_2(user_id=user_id)
#         return jsonify(data), 200 # или можно просто return data,200 ???
#     except Exception as ex:
#         logger.error(ex)
#         return jsonify({"error": ex}), 404
