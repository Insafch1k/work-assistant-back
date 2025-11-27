from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.routes.chat.chat_schemas import CreateChatValidateSchema, SendMessageValidateSchema
from project.domain.chat.chat_bl import ChatBl
from project.utils.data_state import DataFailedMessage

chat_router = Blueprint("chat_router", __name__)

@chat_router.route('/chats', methods=["GET"])
@jwt_required()
def get_chats():
    try:
        user_id = get_jwt_identity()
        data_state = ChatBl.get_user_chats(user_id)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка при получении чатов", error=e).to_response()

@chat_router.route('/chats', methods=["POST"])
@jwt_required()
def create_chat():
    try:
        user_id = get_jwt_identity()
        json_data = request.get_json()
        validate_data_state = CreateChatValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        data_state = ChatBl.create_new_chat(validate_data_state.data,user_id)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка при получении чатов", error=e).to_response()

@chat_router.route('/chats/<int:penpal_id>/messages', methods=["GET"])
@jwt_required()
def get_chat_history(penpal_id: int):
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        new_job_id =  int(request.args.get("new_job_id"))
    except ValueError:
        return DataFailedMessage("limit/offset must be integers",code=400)

    try:
        user_id = get_jwt_identity()
        data_state = ChatBl.get_chat_history(user_id,penpal_id,limit, offset, new_job_id)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка при получении истории чата", error=e).to_response()

@chat_router.route('/chats/<int:penpal_id>/messages', methods=["POST"])
@jwt_required()
def send_message(penpal_id: int):
    try:
        user_id = get_jwt_identity()
        json_data = request.get_json()
        validate_data_state = SendMessageValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        data_state = ChatBl.send_message(validate_data_state.data, penpal_id, user_id)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка при получении истории чата", error=e).to_response()