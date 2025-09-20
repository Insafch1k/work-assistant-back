from functools import wraps

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.DAL.admin_dal import AdminDAL
from project.utils.data_state import DataSuccess

admin_router = Blueprint("admin_router", __name__)

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_tg = get_jwt_identity()
            if not AdminDAL.is_admin(current_tg):
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

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

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    limit = data.get('limit', 20)
    offset = data.get('offset', 0)
    name_filter = data.get('name_filter')

    data_state = AdminDAL.get_users_by_name(offset,limit,name_filter)

    if isinstance(data_state, DataSuccess):
        return jsonify({
            "data": data_state.data
        }), 200
    return jsonify({
            "error": data_state.error_message
        }), 400



@admin_router.route('/admin/ban_user', methods=['POST'])
@admin_required()
def ban_user():
    """
    Бан пользователя
    Параметры:
        user_id
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    data_state = AdminDAL.ban_user(user_id)
    if isinstance(data_state, DataSuccess):
        return jsonify({
            "message": f"User '{user_id}' banned successfully"
        }), 200
    return jsonify({
        "message": data_state.error_message
    }), 400


@admin_router.route('/admin/unban_user', methods=['POST'])
@admin_required()
def unban_user():
    """
    анбан пользователя
    Параметры:
        user_id
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    data_state = AdminDAL.unban_user(user_id)
    if isinstance(data_state, DataSuccess):
        return jsonify({
            "message": f"User '{user_id}' unbanned successfully"
        }), 200
    return jsonify({
        "message": data_state.error_message
    }), 400

