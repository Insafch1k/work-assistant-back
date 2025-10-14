from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from project.application.routes.authorization.auth_schemas import RegisterTgValidateSchema, LoginTgValidateSchema
from project.domain.authorization.auth_bl import AuthBl
from project.utils.data_state import DataFailedMessage

auth_router = Blueprint("auth_router", __name__)

@auth_router.route("/auth/init", methods=["POST"])
def register():
    """
    Регистрация пользователей
    :param: {
        tg_id,
        tg_username,
        user_name,
        user_role
    }
    :return:
    """
    try:
        data = request.get_json()
        validate_data_state = RegisterTgValidateSchema.from_request(data)

        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        data_state = AuthBl.add_user(result.tg_id,result.tg_username,result.user_name,result.user_role)
        if data_state:
            user = data_state.data
       # MetricsBL.track_metric(MetricEvents.UserRegistered, user['user_id'])
            access_token = create_access_token(identity=user.id,additional_claims={'user_role': user.user_role})
            return jsonify({
                "message": "Вы успешно зарегистрированы",
                "access_token": access_token
            }), 200

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка регистрации", error=e).to_response()

@auth_router.route("/auth/login", methods=["POST"])
def login():
    """
    Авторизация пользователей
        :param: {
        tg_id,
        tg_username
    }
    :return:
    """
    try:
        data = request.get_json()
        validate_data_state = LoginTgValidateSchema.from_request(data)

        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        data_state = AuthBl.update_user(result.tg_id,result.tg_username)

        if not data_state:
            return data_state

        user = data_state.data
        access_token = create_access_token(identity=str(user.id),additional_claims={'user_role': user.user_role})
        return jsonify({
            "message": "Вы успешно авторизовались",
            "access_token": access_token,
            "role": user.user_role
        }), 200
    except Exception as e:
        return DataFailedMessage(f"Ошибка при входе в аккаунт", error=e).to_response()