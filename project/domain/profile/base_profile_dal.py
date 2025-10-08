from loguru import logger

from project.domain.core.exceptions import DataBaseError
from project.domain.core.models.user import User
from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import connection_db

class BaseProfileDal:
    @staticmethod
    def get_user_1(user_id) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error") # когда создается DataFailedMessage автоматом ошибка логируется

        with Session() as session:
            try:
                user = session.get(User,user_id)
                if not user:
                    return DataFailedMessage("user not found")

                return DataSuccess(user)
            except Exception as e:
                return DataFailedMessage(f"Database error: {str(e)}")
            
    @staticmethod
    def get_user_2(user_id) -> User:
        Session = connection_db()
        if not Session:
            raise DataBaseError("Database connection error")

        with Session() as session:
            try:
                user = session.get(User,user_id)
                if not user:
                    raise DataBaseError("user not found")

                return user
            except Exception as e:
                raise DataBaseError(f"Database error: {str(e)}")
