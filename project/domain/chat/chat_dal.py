from requests import session
from sqlalchemy import func, case

from project.domain.core.models.chat import ChatModel
from project.domain.core.models.jobs import JobModel
from project.domain.core.models.message import MessageModel
from project.utils.data_state import DataFailedMessage, DataSuccess
from project.utils.db_connection import connection_db, connection_redis


class ChatDal:
    @staticmethod
    def get_user_chats(user_id: int):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                last_msg_subq = (
                    session.query(
                        MessageModel.chat_id.label("chat_id"),
                        func.max(MessageModel.id).label("last_message_id"),
                    )
                    .group_by(MessageModel.chat_id)
                    .subquery()
                )

                #Кол-во непрочитанных сообщений
                last_read_id_expr = case(
                    (ChatModel.finder_id == user_id, ChatModel.last_message_finder),
                    (ChatModel.employer_id == user_id, ChatModel.last_message_employer),
                    else_=None
                )

                unread_count_subq = (
                    session.query(func.count(MessageModel.id))
                    .filter(
                        MessageModel.chat_id == ChatModel.id,
                        MessageModel.sender_id != user_id,
                        MessageModel.id > last_read_id_expr,
                    )
                    .correlate(ChatModel)    # важное место: подзапрос коррелирован с ChatModel
                    .scalar_subquery()
                ).label("unread_count")

                # основной запрос:
                # чаты текущего пользователя + join на последнее сообщение
                query = (
                    session.query(ChatModel, MessageModel, unread_count_subq)
                    .outerjoin(
                        last_msg_subq,
                        ChatModel.id == last_msg_subq.c.chat_id,
                    )
                    .outerjoin(
                        MessageModel,
                        MessageModel.id == last_msg_subq.c.last_message_id,
                    )
                    .filter(
                        (ChatModel.finder_id == user_id)
                        | (ChatModel.employer_id == user_id)
                    )
                    # сортировка по времени последнего сообщения (чаты без сообщений — в конец)
                    .order_by(
                        func.coalesce(MessageModel.id, 0).desc()
                    )
                )

                rows = query.all()

                result = []

                for chat, last_message, unread_count in rows:
                    chat_dict = {
                        "penpal_id": chat.finder_id if user_id == chat.employer_id else chat.employer_id,
                        "name": chat.name,
                        "job_id": chat.job_id,
                        'unread_messages': unread_count,
                        "last_message_data": {
                            "sender_id": last_message.sender_id,
                            "text": last_message.text,
                            "created_at": (
                                last_message.created_at
                            ),
                        }
                    }

                    result.append(chat_dict)

                return DataSuccess(result)

            except Exception as e:
                # здесь можешь добавить логирование
                return DataFailedMessage(
                    "Ошибка при получении списка чатов пользователя",
                    error=e,
                )

    @staticmethod
    def get_chat_history(user_id: int,user_role: str, penpal_id: int, limit: int, offset: int,new_job_id: int = None):
        finder_id = user_id
        employer_id = penpal_id
        if user_role == 'employer':
            finder_id = penpal_id
            employer_id = user_id

        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                chat = session.query(ChatModel).filter(ChatModel.finder_id == finder_id and ChatModel.employer_id == employer_id).first()
                if not chat:
                    return DataFailedMessage('Такого чата нету',code=404)

                messages = session.query(MessageModel).filter(
                    MessageModel.chat_id == chat.id).order_by(MessageModel.id.desc()).offset(offset).limit(limit).all()
                messages = list(reversed(messages))

                result ={
                    "messages": [
                                    {
                                        "sender_id": m.sender_id,
                                        "text": m.text,
                                        "created_at": m.created_at,
                                        "is_readed": m.id > (chat.last_message_finder_id if user_role == 'employer' else chat.last_message_employer_id) or m.sender_id != user_id
                                    }
                                    for m in messages
                                ],
                    "chat": {
                                "penpal_id": chat.finder_id if user_id == chat.employer_id else chat.employer_id,
                                "name": chat.name,
                                "job_id": chat.job_id
                            }
                }

                other_msgs = [m.id for m in messages if m.sender_id != user_id]
                if other_msgs:
                    if user_role == 'employer':
                        chat.last_message_employer_id = other_msgs[-1]
                    else:
                        chat.last_message_finder_id = other_msgs[-1]

                if new_job_id:
                    chat.job_id = new_job_id
                    chat.name = session.get(JobModel, new_job_id).title

                session.commit()

                return DataSuccess(result)
            except Exception as e:
                session.rollback()
                return DataFailedMessage(
                    "Ошибка при получении истории чата",
                    error=e,
                )

    @staticmethod
    def create_new_chat(user_id: int, user_role: str, penpal_id: int, job_id: int):
        finder_id = user_id
        employer_id = penpal_id
        if user_role == 'employer':
            finder_id = penpal_id
            employer_id = user_id

        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                chat = session.query(ChatModel).filter(ChatModel.finder_id == finder_id and ChatModel.employer_id == employer_id).first()
                if chat:
                    return DataFailedMessage('Чат уже существует',code=406)

                job = session.get(JobModel, job_id)
                new_chat = ChatModel(finder_id=finder_id, employer_id=employer_id,name=job.title)
                session.add(new_chat)
                session.commit()

                result = {
                            "chat": {
                                        "penpal_id": chat.finder_id if user_id == chat.employer_id else chat.employer_id,
                                        "name": chat.name,
                                        "job_id": chat.job_id
                                    }
                        }
                return DataSuccess(result)
            except Exception as e:
                return DataFailedMessage(
                    "Ошибка при создании чата",
                    error=e,
                )

    @staticmethod
    def send_message(user_id, penpal_id, text,user_role):
        finder_id = user_id
        employer_id = penpal_id
        if user_role == 'employer':
            finder_id = penpal_id
            employer_id = user_id

        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                chat = session.query(ChatModel).filter(ChatModel.finder_id == finder_id and ChatModel.employer_id == employer_id).first()
                if not chat:
                    return DataFailedMessage('Такого чата нету',code=404)

                if not user_id in [chat.finder_id,chat.employer_id]:
                    return DataFailedMessage('Нет доступа к чату',code=403)

                message = MessageModel(chat_id=chat.id,sender_id=user_id,text=text)
                session.add(message)
                session.commit()

                return DataSuccess('Собщение успешно отправлено')
            except Exception as e:
                session.rollback()
                return DataFailedMessage(
                    "Ошибка при отправке сообщения",
                    error=e,
                )

    @staticmethod
    def get_websocket_sid(user_id):
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"active_users:{user_id}"
            sid = redis_client.get(key)
            return DataSuccess(sid)
        except Exception as e:
            return DataFailedMessage(f"Ошибка при получении websocket sid",error=e)