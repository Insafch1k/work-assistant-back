from project.application.entities.cities import City
from project.application.entities.job import Job
from project.application.routes.jobs.jobs_schemas import GetJobsValidateSchema
from project.domain.cities.cities_bl import CityBl
from project.domain.jobs.base_job_dal import BaseJobDal
from project.domain.profile.get_role import get_user_role
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from loguru import logger


class BaseJobBl:
    @staticmethod
    def add_job(user_id, job_data) -> DataState[City]:
        # city_state = CityBl.get_city_id_by_name(job_data.city)
        # if not city_state:
        #     return DataFailedMessage(error_message=f"Не удалось получить информацию о городе {city_state}")
        # city = city_state.data
        # job = Job.model_validate({
        #     **job_data.model_dump(),
        #     'user_id': user_id,
        #     'city_id': city.id
        # })
        return BaseJobDal.add_job(user_id, job_data)

    @staticmethod
    def get_cities() -> DataState[City]:
        return BaseJobDal.get_cities()

    @staticmethod
    def get_all_info_job(user_id, job_id) -> DataState[Job]:
        job = BaseJobDal.get_all_info_job(user_id, job_id)
        # job = job.data
        # logger.info(f"Экземпляр Job: {job}")
        #
        # city_state = CityBl.get_city_name_by_id(job.city)
        # if not city_state:
        #     return DataFailedMessage(error_message=f"Не удалось получить информацию о городе {city_state}")
        # city_name = city_state.data
        # job['city'] = city_name

        return job

    @staticmethod
    def get_all_jobs(user_id, result: GetJobsValidateSchema) -> DataState:
        return BaseJobDal.get_all_jobs(user_id, result.search, result.employer_id, result.time_start, result.time_end, result.car, result.is_urgent, result.salary, result.age, result.xp, result.date,result.city_id, result.address, result.wanted_job)

    @staticmethod
    def get_my_jobs(user_id) -> DataState:
        user_role = get_user_role(user_id)
        if user_role != "employer":
            return DataFailedMessage('У соискателя не могут быть свои объявления!', code=406)
        return BaseJobDal.get_my_jobs(user_id)

    @staticmethod
    def update_job(job_id, user_id, updated_data) -> DataState:
        job_data = updated_data.get('job', {})
        return BaseJobDal.update_job(job_id, user_id, job_data)

    @staticmethod
    def delete_job(job_id, user_id) -> DataState:
        return BaseJobDal.delete_job(job_id, user_id)



