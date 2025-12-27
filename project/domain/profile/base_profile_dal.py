from project.application.entities.user import User
from project.domain.core.exceptions import DataBaseError
from project.domain.core.models.user import UserModel
from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import connection_db

class BaseProfileDal:
    @staticmethod
    def get_user(user_id) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error") # когда создается DataFailedMessage автоматом ошибка логируется

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                if not user:
                    return DataFailedMessage("Пользователь не найден")

                return DataSuccess(User.model_validate(user))
            except Exception as e:
                return DataFailedMessage(f'Не удалось получить данные о пользователе с id = {user_id}',error=e)

    @staticmethod
    def update_avatar(user_id,avatar_url) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                old_photo = user.photo
                user.photo = avatar_url
                session.commit()
                return DataSuccess(old_photo)
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при обновлении фото пользователя",error=e)


    @staticmethod
    def change_role(user_id, user_role) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error") # когда создается DataFailedMessage автоматом ошибка логируется

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                if not user:
                    return DataFailedMessage("Пользователь не найден")

                user.user_role = user_role
                session.commit()

                return DataSuccess(f'Роль успешно изменена на {user.user_role}')
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f'Не удалось поменять роль у пользователя с id = {user_id}',error=e)
            
    # @staticmethod
    # def get_user_2(user_id) -> User:
    #     Session = connection_db()
    #     if not Session:
    #         raise DataBaseError("Database connection error")
    #
    #     with Session() as session:
    #         try:
    #             user = session.get(User,user_id)
    #             if not user:
    #                 raise DataBaseError("user not found")
    #
    #             return user
    #         except Exception as e:
    #             raise DataBaseError(f"Database error: {str(e)}")
