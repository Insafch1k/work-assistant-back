from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from project.application.routes.admin.admin_schemas import GetUsersValidateSchema, BanUserValidateSchema
from project.domain.admin.admin_bl import AdminBl
from project.domain.authorization.auth_bl import AuthBl
from project.utils.data_state import  DataFailedMessage
from project.utils.is_admin import admin_required

admin_router = Blueprint("admin_router", __name__)


@admin_router.route('/is_admin', methods=["GET"])
@jwt_required()
def check_is_admin():
    try:
        user_id = get_jwt_identity()
        admin_data_state = AdminBl.is_admin(user_id)
        if not admin_data_state:
            return admin_data_state.to_response()

        response_data = {
            "is_admin": admin_data_state.data
        }

        return jsonify(response_data), 200
    except Exception as e:
        return DataFailedMessage("Ошибка проверки админ прав", error=e).to_response()

@admin_router.route('/admin/get_users', methods=['POST'])
@admin_required()
def get_users():
    """
    Получение списка пользователей
    Параметры:
        limit: сколько пользователей вернуть
        offset: смещение для пагинации (по умолчанию 0)
        name_filter: фильтр по имени (содержит подстроку)
    :return: список пользователей
    """

    try:
        json_data = request.get_json()
        validate_data_state = GetUsersValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        admin_data_state = AdminBl.get_users_by_name(result)
        return admin_data_state.to_response()

    except Exception as e:
        return DataFailedMessage("Ошибка проверки админ прав", error=e).to_response()



@admin_router.route('/admin/ban_user', methods=['POST'])
@admin_required()
def ban_user():
    """
    Бан пользователя
    Параметры:
        user_id
    """
    try:
        json_data = request.get_json()
        validate_data_state = BanUserValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        admin_data_state = AdminBl.set_ban_status(user_id=result.user_id,is_banned=True)
        return admin_data_state.to_response()

    except Exception as e:
        return DataFailedMessage("Ошибка при блокировке пользователя", error=e).to_response()


@admin_router.route('/admin/unban_user', methods=['POST'])
@admin_required()
def unban_user():
    """
    анбан пользователя
    Параметры:
        user_id
    """
    try:
        json_data = request.get_json()
        validate_data_state = BanUserValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        admin_data_state = AdminBl.set_ban_status(user_id=result.user_id, is_banned=False)
        return admin_data_state.to_response()

    except Exception as e:
        return DataFailedMessage("Ошибка при разблокировке пользователя", error=e).to_response()