from project.domain.core.exceptions import DataBaseError
from project.domain.core.models.resume import Resume
from project.domain.profile.base_profile_dal import BaseProfileDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from project.utils.db_connection import connection_db


class EmployerProfileDal(BaseProfileDal):
    pass
    # @staticmethod
    # def update_finder_profile(age, user_id):
    #     Session = connection_db()
    #     if not Session:
    #         return DataFailedMessage("Database connection error")
    #
    #     with Session() as session:
    #         try:
    #             user = session.get(User, user_id).filter(User.tg == tg_id).first()
    #             if not user:
    #                 return DataFailedMessage("user not found")
    #
    #             return DataSuccess(user)
    #         except Exception as e:
    #             return DataFailedMessage(f"Database error: {str(e)}")
    #
    #         with conn.cursor() as cur:
    #             stat = """UPDATE finders SET age = %s WHERE user_id = %s"""
    #             cur.execute(stat, (age, user_id,))
    #             conn.commit()
    #             print(f"Данные соискателя успешно обновлены!")
    #     except Exception as e:
    #         Logger.error(f"Error update finder profile {str(e)}")
    #         conn.rollback()
    #         return None
    #     finally:
    #         conn.close()
    @staticmethod
    def get_resume_1(user_id) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                resume = session.query(Resume).filter(Resume.user_id == user_id).first()
                if not resume:
                    return DataFailedMessage("resume not found")

                return DataSuccess(resume)
            except Exception as e:
                return DataFailedMessage(f"Database error: {str(e)}")

    @staticmethod
    def get_resume_2(user_id) -> Resume:
        Session = connection_db()
        if not Session:
            raise DataBaseError("Database connection error")

        with Session() as session:
            try:
                resume = session.query(Resume).filter(Resume.user_id == user_id).first()
                if not resume:
                    raise DataBaseError("resume not found")

                return resume
            except Exception as e:
                raise DataBaseError(f"Database error: {str(e)}")