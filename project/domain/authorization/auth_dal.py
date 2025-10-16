from datetime import datetime
from loguru import logger
from project.application.entities.user import User
from project.domain.core.models.resume import ResumeModel
from project.domain.core.models.user import UserModel
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from project.utils.db_connection import connection_db

class AuthDal:
    @staticmethod
    def add_user(tg_id, tg_username,user_name, user_role) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = UserModel(
                    user_role=user_role,
                    tg_username=tg_username,
                    tg_id=tg_id,
                    user_name=user_name)
                session.add(user)
                session.flush() # Синхронизирует состояние сессии с БД  Все изменения в сессии перенесутся в БД, но не зафиксируются
                resume = ResumeModel(
                    user_id=user.id)
                session.add(resume)
                session.commit()

                logger.info(f"Пользователь {user.user_name} успешно добавлен с ID: {user.id}")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при добавлении пользователя",error=e)


    @staticmethod
    def update_user(tg_id, tg_username) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.query(UserModel).filter(UserModel.tg_id == tg_id).first()
                if not user:
                    return DataFailedMessage("Пользователь не найден")

                user.tg_username = tg_username
                user.last_login_at = datetime.now()
                session.commit()

                #logger.info(f"Пользователь {user.user_name} успешно вошел в аккаунт")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при обновлении пользователя",error=e)
