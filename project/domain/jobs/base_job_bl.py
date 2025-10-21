from project.application.entities.job import Job
from project.domain.cities.cities_bl import CityBl
from project.domain.jobs.base_job_dal import BaseJobDal
from project.utils.data_state import DataState


class BaseJobBl:
    @staticmethod
    def add_job(user_id, job_data) -> DataState[Job]:
        pass
        # city_state = CityBl.get_city_id_by_name(job_data.city)
        # if not city_state:
        #     return city_state
        # city = city_state.data
        # job = Job(user_id=user_id,
        #           city_id=city.id,
        #           title=job_data.title
        #           ...) # или типа job = Job.from_user_id_and_data(user_id, job_data)
        # return BaseJobDal.add_job(job)