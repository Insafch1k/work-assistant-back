from sqlalchemy import update, and_, case
from sqlalchemy.orm import aliased

from project.application.entities.job import Job, JobBaseInfo, JobInfo
from project.domain.core.models.job_favorite import JobFavoriteModel
from project.domain.core.models.jobs import JobModel
from project.domain.core.models.user import UserModel
from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import connection_db

from loguru import logger


class BaseJobDal:
    @staticmethod
    def add_job(job_data):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                job = JobModel(user_id=job_data.user_id,
                                city_id=job_data.city_id,
                                title=job_data.title,
                                wanted_job=job_data.wanted_job,
                                description=job_data.description,
                                salary=job_data.salary,
                                date=job_data.date,
                                time_start=job_data.time_start,
                                time_end=job_data.time_end,
                                address=job_data.address,
                                is_urgent=job_data.is_urgent,
                                xp=job_data.xp,
                                age=job_data.age,
                                car=job_data.car)
                session.add(job)
                session.commit()

                logger.info(f"Вакансия '{job.title}' успешно добавлена с ID: {job.id}")
                return DataSuccess(Job.model_validate(job).to_json())
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при добавлении вакансии", error=e)

    @staticmethod
    def delete_job(job_id, user_id):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                job = session.get(JobModel, job_id)

                if job.user_id != int(user_id):
                    return DataFailedMessage("Нет доступа",code=406)

                session.delete(job)
                session.commit()
                return DataSuccess('Вакансия удалена')
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при удалении вакансии", error=e)

    @staticmethod
    def get_all_info_job(user_id, job_id):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                FavoriteAlias = aliased(JobFavoriteModel)
                row = (
                    session.query(JobModel,
                                  UserModel,
                                  case(
                                      (FavoriteAlias.id.isnot(None), True),
                                      else_=False
                                  ).label("is_favorite"))
                    .join(UserModel, UserModel.id == JobModel.user_id)
                    .outerjoin(
                        FavoriteAlias,
                        and_(
                            FavoriteAlias.job_id == JobModel.id,
                            FavoriteAlias.user_id == int(user_id)
                        )
                    ).where(JobModel.id == job_id)
                    .first()
                )
                job, user, is_favorite = row

                if not job:
                    return DataFailedMessage(f"Вакансия с id {job_id} не найдена")

                job_data = JobInfo(
                    id=job.id,
                    user=user,
                    city_id=job.city_id,
                    title=job.title,
                    wanted_job=job.wanted_job,
                    description=job.description,
                    salary=job.salary,
                    date=job.date,
                    time_start=job.time_start,
                    time_end=job.time_end,
                    address=job.address,
                    is_urgent=job.is_urgent,
                    status=job.status,
                    xp=job.xp,
                    age=job.age,
                    created_at=job.created_at,
                    car=job.car,
                    is_favorite=is_favorite,
                ).model_dump()

                return DataSuccess(job_data)

            except Exception as e:
                return DataFailedMessage("Ошибка при получении вакансии", error=e)
    @staticmethod
    def get_all_jobs(user_id, search, employeer_id):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                FavoriteAlias = aliased(JobFavoriteModel)
                query = session.query( JobModel,UserModel,
                    case(
                (FavoriteAlias.id.isnot(None), True),
                    else_=False
                    ).label("is_favorite"))

                if search:
                    search_term = f"%{search.strip()}%"
                    query = query.filter(JobModel.title.ilike(search_term))

                if employeer_id:
                    query = query.filter(JobModel.user_id == employeer_id)

                jobs = (
                    query.join(UserModel, UserModel.id == JobModel.user_id)
                    .outerjoin(
                        FavoriteAlias,
                        and_(
                            FavoriteAlias.job_id == JobModel.id,
                            FavoriteAlias.user_id == user_id
                        )
                    )
                    .all()
                )

                if not jobs:
                    return DataSuccess({"jobs": []})
                    #return DataFailedMessage("Ошибка в нахождении списка вакансий")

                # Преобразуем результат в JSON
                jobs_json = []
                for job, user, is_favorite in jobs:
                    jobs_json.append(
                        JobBaseInfo(
                            id=job.id,
                            user=user,
                            title=job.title,
                            salary=job.salary,
                            time_start=job.time_start,
                            time_end=job.time_end,
                            address=job.address,
                            is_urgent=job.is_urgent,
                            car=job.car,
                            is_favorite=is_favorite,
                        ).model_dump()
                    )

                return DataSuccess({"jobs":jobs_json})
            except Exception as e:
                return DataFailedMessage(f"Ошибка при получении всех вакансии", error=e)

    @staticmethod
    def update_job(job_id, user_id, job_data) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")
        if not job_data:
            return DataFailedMessage("Нет данных для обновления")

        with Session() as session:
            try:
                job = session.get(JobModel, job_id)
                if not job:
                    return DataFailedMessage("Вакансия не найдена")
                if job.user_id != int(user_id):
                    return DataFailedMessage("Нет доступа",code=406)

                stmt = (
                    update(JobModel)
                    .where(JobModel.id == job_id)
                    .values(**job_data)
                )
                session.execute(stmt)
                session.commit()

                session.commit()
                return DataSuccess('Данные вакансии успешно обновлены!')
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка в обновлении вакансии job_id = {job_id}", error=e)