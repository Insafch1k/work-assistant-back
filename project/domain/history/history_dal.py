from datetime import datetime

from sqlalchemy import and_, func, case
from sqlalchemy.orm import aliased

from project.application.entities.job import Job, JobBaseInfo
from project.application.entities.job_favorite import JobFavorite
from project.domain.core.models.cities import CityModel
from project.domain.core.models.job_favorite import JobFavoriteModel
from project.domain.core.models.job_view_history import JobViewHistoryModel
from project.domain.core.models.jobs import JobModel
from project.domain.core.models.user import UserModel
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

                FavoriteAlias = aliased(JobFavoriteModel)

                history_jobs = (
                    session.query(JobModel, case(
                (FavoriteAlias.id.isnot(None), True),
                    else_=False
                    ).label("is_favorite"),UserModel,CityModel)
                    .outerjoin(
                        FavoriteAlias,
                        and_(
                            FavoriteAlias.job_id == JobModel.id,
                            FavoriteAlias.user_id == user_id
                        )
                    )
                    .join(UserModel, UserModel.id == JobModel.user_id)
                    .join(CityModel, CityModel.id == JobModel.city_id)
                    .join(JobViewHistoryModel, JobViewHistoryModel.job_id == JobModel.id)
                    .filter(JobViewHistoryModel.user_id == int(user_id))
                    .all()
                )

                if not history_jobs:
                    return DataSuccess([])

                jobs_data = []
                for job, is_favorite, user, city in history_jobs:
                    jobs_data.append(
                        JobBaseInfo(
                            id=job.id,
                            user=user,
                            is_favorite=is_favorite,
                            title=job.title,
                            salary=job.salary,
                            city=city.name,
                            time_start=job.time_start,
                            time_end=job.time_end,
                            address=job.address,
                            is_urgent=job.is_urgent,
                            car=job.car
                        ).model_dump())

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