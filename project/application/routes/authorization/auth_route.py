from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token, get_jwt
from flask_socketio import disconnect, emit
from loguru import logger

from extensions import socketio
from project.application.entities.event import MetricEvents
from project.application.routes.authorization.auth_schemas import RegisterTgValidateSchema, LoginTgValidateSchema, \
    RegistrationValidateSchema, ConfirmationValidateSchema, LoginValidateSchema, ForgotPasswordValidateSchema, \
    RecoveryPasswordValidateSchema, ChangePasswordValidateSchema
from project.application.routes.metrics.metric_schemas import TrackEventValidateSchema
from project.domain.authorization.auth_bl import AuthBl
from project.domain.metrics.metric_bl import MetricsBL
from project.utils.data_state import DataFailedMessage
from project.utils.get_jwt_from_socket import require_jwt_or_disconnect

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
    {temporary_id: int}
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
        return jsonify({
            "temporary_id": temporary_id
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка регистрации", error=e).to_response()

@auth_router.route("/auth/confirm_mail", methods=['POST'])
def confirm_email():
    """
    Подтверждение почты по коду
    {
        'temporary_id': int,
        'code': int,
    }
    :return:
            "message": str,
            "access_token": str,
            "role": str
    """
    try:
        json_data = request.get_json()
        validate_data_state= ConfirmationValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.confirm_mail(result)
        if not auth_data_state:
            return auth_data_state.to_response()

        user = auth_data_state.data
        MetricsBL.track_metric(
            TrackEventValidateSchema(event_name=MetricEvents.UserRegistered, user_id=user.id))
        access_token = create_access_token(identity=str(user.id))
        decoded = decode_token(access_token)
        token_data_state = AuthBl.add_token(user_id=user.id,jti=decoded["jti"])
        if not token_data_state:
            return token_data_state.to_response()

        return jsonify({
            "message": "Вы успешно зарегистрированы",
            "access_token": access_token,
            "role": user.user_role
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при подтверждении почты", error=e).to_response()


@auth_router.route("/auth/forgot_password", methods=['POST'])
def forgot_password():
    """
   Восстановление пароля, отправляет код на почту. Возвращает temporary_id, который нужен будет в запросе recovery_code
    {
        'email': str,
    }
    :return:
    {"temporary_id": int}
    """
    try:
        json_data = request.get_json()
        validate_data_state= ForgotPasswordValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.forgot_password(result)
        if not auth_data_state:
            return auth_data_state.to_response()

        return jsonify({
            "temporary_id": auth_data_state.data,
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при восстановлении пароля", error=e).to_response()

@auth_router.route("/auth/recovery_code", methods=['POST'])
def check_recovery_code():
    """
    проверка кода для восстановления пароля
    {
        'temporary_id': int,
        'code': int,
    }
    :return:
    """
    try:
        json_data = request.get_json()
        validate_data_state = ConfirmationValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.check_recovery_code(result)
        if not auth_data_state:
            return auth_data_state.to_response()

        return jsonify({
            "message":'Верный код',
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при восстановлении пароля", error=e).to_response()

@auth_router.route("/auth/recovery_password", methods=['POST'])
def recovery_password():
    """
    восстановление пароля
    {
        'temporary_id': int,
        'code': int,
        'password': str
    }
    :return:
            "message": str,
            "access_token": str,
            "role": str
    """
    try:
        json_data = request.get_json()
        validate_data_state = RecoveryPasswordValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.recovery_password(result)
        if not auth_data_state:
            return auth_data_state.to_response()

        user = auth_data_state.data
        token_data_state = AuthBl.delete_all_sessions(user_id=user.id)
        if not token_data_state:
            return token_data_state.to_response()

        access_token = create_access_token(identity=str(user.id))
        decoded = decode_token(access_token)
        token_data_state = AuthBl.add_token(user_id=user.id,jti=decoded["jti"])
        if not token_data_state:
            return token_data_state.to_response()

        return jsonify({
            "message": "Вы успешно восстановили аккаунт.",
            "access_token": access_token,
            "role": user.user_role
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при восстановлении пароля", error=e).to_response()


@auth_router.route("/auth/change_password", methods=['POST'])
@jwt_required()
def change_password():
    """
    Смена пароля
    {
        'old_password': str,
        'new_password': str
    }
        :return:
            "message": str,
            "access_token": str,
            "role": str
    """
    try:
        json_data = request.get_json()
        user_id = get_jwt_identity()
        validate_data_state = ChangePasswordValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        auth_data_state = AuthBl.change_password(result,user_id)
        if not auth_data_state:
            return auth_data_state.to_response()

        user = auth_data_state.data
        token_data_state = AuthBl.delete_all_sessions(user_id=user.id)
        if not token_data_state:
            return token_data_state.to_response()

        access_token = create_access_token(identity=str(user.id))
        decoded = decode_token(access_token)
        token_data_state = AuthBl.add_token(user_id=user.id,jti=decoded["jti"])
        if not token_data_state:
            return token_data_state.to_response()

        return jsonify({
            "message": "Вы успешно сменили пароль.",
            "access_token": access_token,
            "role": user.user_role
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при смене пароля", error=e).to_response()

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
        MetricsBL.track_metric(TrackEventValidateSchema(event_name=MetricEvents.UserRegistered,user_id=user.id))
        access_token = create_access_token(identity=str(user.id))
        decoded = decode_token(access_token)
        token_data_state = AuthBl.add_token(user_id=user.id,jti=decoded["jti"])
        if not token_data_state:
            return token_data_state.to_response()

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
        decoded = decode_token(access_token)
        token_data_state = AuthBl.add_token(user_id=user.id,jti=decoded["jti"])
        if not token_data_state:
            return token_data_state.to_response()

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
    Авторизация пользователя
        :param: {
        email,
        password
    }
       :return:
            "message": str,
            "access_token": str,
            "role": str
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
        decoded = decode_token(access_token)
        token_data_state = AuthBl.add_token(user_id=user.id,jti=decoded["jti"])
        if not token_data_state:
            return token_data_state.to_response()

        return jsonify({
            "message": "Вы успешно авторизовались",
            "access_token": access_token,
            "role": user.user_role
        }), 200
    except Exception as e:
        return DataFailedMessage(f"Ошибка при входе в аккаунт", error=e).to_response()

@auth_router.route("/auth/logout", methods=['GET'])
@jwt_required()
def logout():
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()  # Полный payload токена
        auth_data_state = AuthBl.delete_token(user_id=user_id, jti=jwt_data["jti"])
        if not auth_data_state:
            return auth_data_state.to_response()

        return jsonify({
            "message": "Вы вышли из аккаунта.",
        }), 200

    except Exception as e:
        return DataFailedMessage(f"Ошибка при выходе из аккаунта", error=e).to_response()

@socketio.on("connect", namespace="/ws")
def on_connect():
    user_id = require_jwt_or_disconnect()
    if not user_id:
        emit("connected", namespace="/ws")
        disconnect()
        return

    sid = request.sid
    data_state = AuthBl.add_websocket_uid(user_id,sid)

    if not data_state:
        emit("error", data_state.to_response()[0].data, namespace="/ws")
        disconnect()
        return

    emit("connected", namespace="/ws")


@socketio.on("disconnect", namespace="/ws")
def on_disconnect(data):
    logger.debug('leave')
    user_id = require_jwt_or_disconnect()
    #sid = request.sid
    if not user_id:
        return

    AuthBl.delete_websocket_uid(user_id)
    disconnect()
