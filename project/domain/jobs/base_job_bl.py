from project.application.entities.cities import City
from project.application.entities.job import Job
from project.domain.cities.cities_bl import CityBl
from project.domain.jobs.base_job_dal import BaseJobDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess


class BaseJobBl:
    @staticmethod
    def add_job(user_id, job_data) -> DataState[City]:
        pass
        city_state = CityBl.get_city_id_by_name(job_data.city)
        if not city_state:
            return DataFailedMessage(error_message=f"Не удалось получить информацию о городе {city_state}")
        city = city_state.data
        job = Job.model_validate({
            **job_data.model_dump(exclude={'city'}),  # исключаем поле city
            'user_id': user_id,
            'city_id': city.id
        })
        return BaseJobDal.add_job(job)