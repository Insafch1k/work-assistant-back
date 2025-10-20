from project.application.entities.job import Jobs
from project.domain.cities.cities_bl import CityBl
from project.domain.jobs.base_job_dal import BaseJobDal
from project.utils.data_state import DataState


class BaseJobBl:
    @staticmethod
    def add_job(user_id, job_data) -> DataState[Jobs]:
        city_state = CityBl.get_city_id_by_name(job_data.city)
        city_id = city_state.data.id
        job_data.city_id = city_id
        return BaseJobDal.add_job(user_id, job_data)