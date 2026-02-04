from datetime import datetime

from sqlalchemy import and_, func

from project.application.entities.job import Job
from project.application.entities.job_favorite import JobFavorite
from project.domain.core.models.cities import CityModel
from project.domain.core.models.job_favorite import JobFavoriteModel
from project.domain.core.models.job_view_history import JobViewHistoryModel
from project.domain.core.models.jobs import JobModel
from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import connection_db

from loguru import logger

class HistoryDal:

    @staticmethod
    def get_list_of_history_job(user_id):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:

                # Один SQL-запрос: JOIN истории + LEFT JOIN избранного
                history_jobs = (
                    session.query(JobModel, JobFavoriteModel.id.label("favorite_id"))
                    .join(JobViewHistoryModel, JobViewHistoryModel.job_id == JobModel.id)
                    .outerjoin(
                        JobFavoriteModel,
                        and_(
                            JobFavoriteModel.job_id == JobModel.id,
                            JobFavoriteModel.user_id == user_id
                        )
                    )
                    .filter(JobViewHistoryModel.user_id == user_id)
                    .order_by(JobViewHistoryModel.viewed_at.desc())
                    .all()
                )

                if not history_jobs:
                    return DataSuccess([])

                # Формируем JSON
                jobs_data = []
                for job_model, favorite_id in history_jobs:
                    job_data = Job.model_validate(job_model).to_json()
                    job_data["is_favorite"] = favorite_id is not None
                    jobs_data.append(job_data)

                return DataSuccess(jobs_data)

            except Exception as e:
                return DataFailedMessage("Ошибка при получении истории просмотров", error=e)

    @staticmethod
    def add_job_to_history(user_id, job_id):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                job = session.get(JobModel, job_id)
                if not job:
                    return DataFailedMessage("Вакансия не найдена")
                # Проверяем, есть ли запись
                existing = (
                    session.query(JobViewHistoryModel)
                    .filter(
                        and_(
                            JobViewHistoryModel.user_id == user_id,
                            JobViewHistoryModel.job_id == job_id
                        )
                    )
                    .first()
                )

                if existing:
                    # Обновляем дату просмотра
                    existing.viewed_at = func.now()
                else:
                    # Создаём новую запись
                    new_view = JobViewHistoryModel(
                        user_id=user_id,
                        job_id=job_id,
                        viewed_at=func.now()
                    )
                    session.add(new_view)

                session.commit()
                return DataSuccess({"job_id": job_id, "message": "Вакансия добавлена в историю"})

            except Exception as e:
                session.rollback()
                return DataFailedMessage("Ошибка при добавлении вакансии в историю", error=e)