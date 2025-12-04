from extensions import socketio
from project.application.routes.chat.chat_schemas import CreateChatValidateSchema, SendMessageValidateSchema
from project.domain.chat.chat_dal import ChatDal
from project.domain.profile.get_role import get_user_role


class ChatBl:
    @staticmethod
    def get_user_chats(user_id: int):
        return ChatDal.get_user_chats(user_id)

    @staticmethod
    def create_new_chat(result: CreateChatValidateSchema, user_id: int):
        user_role = get_user_role(user_id)
        return ChatDal.create_new_chat(user_id, user_role, result.penpal_id, result.job_id)

    @staticmethod
    def get_chat_history(user_id, penpal_id, limit, offset, new_job_id):
        user_role = get_user_role(user_id)
        return ChatDal.get_chat_history(user_id, user_role, penpal_id, limit, offset, new_job_id)

    @staticmethod
    def send_message(result: SendMessageValidateSchema, penpal_id: int, user_id: int):
        user_role = get_user_role(user_id)
        data_state = ChatDal.send_message(user_id, penpal_id,result.text,user_role)
        if data_state:
            sid_data_state = ChatDal.get_websocket_sid(penpal_id)
            if sid_data_state and sid_data_state.data:
                socketio.emit("ping", {"penpal_id": penpal_id}, to=sid_data_state.data, namespace="/ws")

        return data_state

    @staticmethod
    def add_websocket_connection(user_id: int, sid: str):
        return ChatDal.add_websocket_connection(user_id, sid)