from typing import Optional
from sqlalchemy import select
from project.application.entities.user import User
from project.domain.core.models.user import UserModel
from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import connection_db


class AdminDal:
    @staticmethod
    def is_admin(user_id) -> DataState[bool]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                return DataSuccess(user.is_admin)

            except Exception as e:
                return DataFailedMessage(f"Ошибка при проверки пользователя на админ права", error=e)


    @staticmethod
    def set_ban_status(user_id: int, ban: bool)-> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                user.banned = ban
                session.commit()
                return DataSuccess()

            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при {'раз' if not ban else ''}блокировке пользователя", error=e)

    @staticmethod
    def get_users_by_name(offset: int, limit: int,
    name_filter: Optional[str]) -> DataState[list[User]]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                query = select(UserModel)

                if name_filter:
                    query = query.where(UserModel.user_name.ilike(f"%{name_filter}%"))

                query = query.order_by(UserModel.created_at.desc()).offset(offset).limit(limit)
                users =  session.execute(query).scalars().all()
                return DataSuccess(list(map(lambda user: User.model_validate(user),users)))

            except Exception as e:
                return DataFailedMessage(f"Ошибка при получении списка пользователей", error=e)
