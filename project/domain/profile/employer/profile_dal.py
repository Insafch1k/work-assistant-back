from loguru import logger

from project.application.entities.resume import Resume
from project.domain.core.models.resume import ResumeModel
from project.domain.core.models.user import UserModel
from project.domain.profile.base_profile_dal import BaseProfileDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from project.utils.db_connection import connection_db


class EmployerProfileDal(BaseProfileDal):

    @staticmethod
    def update_profile(user_id, resume_data:dict, profile_data: dict) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                if not user:
                    return DataFailedMessage("Пользователь не найден")

                resume = session.query(ResumeModel).filter(ResumeModel.user_id == user_id).first()
                if not resume:
                    return DataFailedMessage("Резюме не найдено")

                for field, value in profile_data.items():
                    if not hasattr(user, field):
                        logger.warning(f'Поле {field} для таблицы user не найдено')
                        continue
                    setattr(user, field, value)

                for field, value in resume_data.items():
                    if not hasattr(resume, field):
                        logger.warning(f'Поле {field} для таблицы resume не найдено')
                        continue
                    setattr(resume, field, value)

                session.commit()
                return DataSuccess('Данные профиля соискателя успешно обновлены!')
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка в обновлении профиля для user_id = {user_id}",error=e)

    @staticmethod
    def get_resume(user_id) -> DataState[Resume]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                resume = session.query(ResumeModel).filter(ResumeModel.user_id == user_id).first()
                if not resume:
                    return DataFailedMessage("Резюме не найдено")

                return DataSuccess(Resume.model_validate(resume))
            except Exception as e:
                return DataFailedMessage(f"Ошибка в получении резюме для user_id = {user_id}",error=e)

    # @staticmethod
    # def get_resume_2(user_id) -> Resume:
    #     Session = connection_db()
    #     if not Session:
    #         raise DataBaseError("Database connection error")
    #
    #     with Session() as session:
    #         try:
    #             resume = session.query(Resume).filter(Resume.user_id == user_id).first()
    #             if not resume:
    #                 raise DataBaseError("resume not found")
    #
    #             return resume
    #         except Exception as e:
    #             raise DataBaseError(f"Database error: {str(e)}")