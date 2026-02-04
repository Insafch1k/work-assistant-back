from project.application.entities.job import Job
from project.application.entities.job_favorite import JobFavorite
from project.domain.core.models.cities import CityModel
from project.domain.core.models.job_favorite import JobFavoriteModel
from project.domain.core.models.jobs import JobModel
from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import connection_db

from loguru import logger


class FavoriteJobDal:
    @staticmethod
    def add_job_to_favorite(user_id, job_id) -> DataState[JobFavorite]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                job = session.get(JobModel, job_id)
                if not job:
                    return DataFailedMessage("Вакансия не найдена")

                job = session.query(JobFavoriteModel).filter(JobFavoriteModel.user_id == user_id, JobFavoriteModel.job_id == job_id).all()
                if job:
                    return DataFailedMessage("Вакансия уже есть в избранном")

                job_favorite = JobFavoriteModel(user_id=user_id, job_id=job_id)
                session.add(job_favorite)
                session.commit()

                logger.info(f"Вакансия '{job_favorite.job_id}' успешно добавлена в избранное с ID: {job_favorite.id}")
                return DataSuccess(JobFavorite.model_validate(job_favorite).to_json())
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при добавлении вакансии в избранное", error=e)

    @staticmethod
    def get_list_of_favorites(user_id) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                # JOIN запрос между job_favorites и jobs
                favorite_jobs = (session.query(JobModel)
                                 .join(JobFavoriteModel, JobFavoriteModel.job_id == JobModel.id)
                                 .filter(JobFavoriteModel.user_id == user_id)
                                 .all())

                if not favorite_jobs:
                    return DataSuccess([])  # Возвращаем пустой список, если нет избранных

                jobs_data = []
                for job in favorite_jobs:
                    job_data = Job.model_validate(job).to_json()
                    job_data["is_favorite"] = True
                    jobs_data.append(job_data)
                return DataSuccess(jobs_data)
            except Exception as e:
                return DataFailedMessage(f"Ошибка при получении списка избранных вакансий", error=e)

    @staticmethod
    def delete_job_from_favorites(user_id, job_id) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                job_favorite = session.query(JobFavoriteModel).filter_by(
                    user_id=user_id,
                    job_id=job_id
                ).first()

                if not job_favorite:
                    return DataFailedMessage("Вакансия не найдена в избранном")

                session.delete(job_favorite)
                session.commit()

                logger.info(f"Вакансия '{job_id}' удалена из избранного пользователя {user_id}")
                return DataSuccess({"message": "Вакансия успешно удалена из избранного", "deleted_id": job_id})
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при удалении вакансии из избранного", error=e)
