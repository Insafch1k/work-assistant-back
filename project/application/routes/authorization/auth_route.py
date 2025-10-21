from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from project.application.routes.authorization.auth_schemas import RegisterTgValidateSchema, LoginTgValidateSchema, \
    RegistrationValidateSchema, ConfirmationValidateSchema, LoginValidateSchema
from project.domain.authorization.auth_bl import AuthBl
from project.utils.data_state import DataFailedMessage

auth_router = Blueprint("auth_router", __name__)

@auth_router.route("/auth/register_mail", methods=['POST'])
def register_mobile():
    """
    Регистрация пользователя
    {
        'user_name': str,
        'email': str,
        'password': str,
        'user_role': str,
    }
    :return:
    """
    try:
        json_data = request.get_json()
        validate_data_state= RegistrationValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.register_mail(result)
        if not auth_data_state:
            return auth_data_state.to_response()

        temporary_id = auth_data_state.data
        # MetricsBL.track_metric(MetricEvents.UserRegistered, user['user_id'])
        return jsonify({
            "temporary_id": temporary_id
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка регистрации", error=e).to_response()

@auth_router.route("/auth/confirm_mail", methods=['POST'])
def confirm_email():
    """
    Регистрация пользователя
    {
        'temporary_id': int,
        'code': int,
    }
    :return:
    """
    try:
        json_data = request.get_json()
        validate_data_state= ConfirmationValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.confirm_mail(result.temporary_id,result.code)
        if not auth_data_state:
            return auth_data_state.to_response()

        user = auth_data_state.data
        # MetricsBL.track_metric(MetricEvents.UserRegistered, user['user_id'])
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "message": "Вы успешно зарегистрированы",
            "access_token": access_token,
            "role": user.user_role
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при подтверждении почты", error=e).to_response()

@auth_router.route("/auth/register", methods=["POST"])
def register_tg():
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
        data_state = AuthBl.register_tg(result)
        if not data_state:
            return data_state.to_response()

        user = data_state.data
   # MetricsBL.track_metric(MetricEvents.UserRegistered, user['user_id'])
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "message": "Вы успешно зарегистрированы",
            "access_token": access_token,
            "role": user.user_role
        }), 200

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
        data_state = AuthBl.update_user(result)

        if not data_state:
            return data_state.to_response()

        user = data_state.data
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Вы успешно авторизовались",
            "access_token": access_token,
            "role": user.user_role
        }), 200
    except Exception as e:
        return DataFailedMessage(f"Ошибка при входе в аккаунт", error=e).to_response()

@auth_router.route("/auth/login_mail", methods=["POST"])
def login_mail():
    """
    Авторизация пользователей
        :param: {
        email,
        password
    }
    :return:
    """
    try:
        data = request.get_json()
        validate_data_state = LoginValidateSchema.from_request(data)

        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        data_state = AuthBl.check_user(result)

        if not data_state:
            return data_state.to_response()

        user = data_state.data
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Вы успешно авторизовались",
            "access_token": access_token,
            "role": user.user_role
        }), 200
    except Exception as e:
        return DataFailedMessage(f"Ошибка при входе в аккаунт", error=e).to_response()