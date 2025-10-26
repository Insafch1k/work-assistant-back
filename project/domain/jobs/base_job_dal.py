from project.application.entities.job import Job
from project.domain.core.models.jobs import JobModel
from project.utils.data_state import DataFailedMessage, DataSuccess
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
    def get_all_info_job(user_id, job_id):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                job = session.query(JobModel).filter(JobModel.id == job_id).first()
                if not job:
                    return DataFailedMessage(f"Вакансия с id {job_id} не найдена")
                return DataSuccess(Job.model_validate(job).to_json())
            except Exception as e:
                return DataFailedMessage(f"Ошибка при получении вакансии", error=e)



