from project.application.entities.cities import City
from project.application.entities.job import Job
from project.application.entities.job_favorite import JobFavorite
from project.domain.cities.cities_bl import CityBl
from project.domain.favorite.favorite_dal import FavoriteJobDal
from project.domain.history.history_dal import HistoryDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from loguru import logger

class HistoryBl:
    @staticmethod
    def get_list_of_jobs_history(user_id):
        return HistoryDal.get_list_of_history_job(user_id)
        # jobs = jobs_state.data
        # logger.info(f"Список истории: {jobs}")
        # for job in jobs:
        #     city_state = CityBl.get_city_name_by_id(job['city_id'])
        #     if not city_state:
        #         return DataFailedMessage(error_message=f"Не удалось получить информацию о городе {city_state}")
        #     city_name = city_state.data
        #     job['city'] = city_name
        #
        # return DataSuccess(jobs)
    @staticmethod
    def add_job_to_history(user_id, job_id):
        return HistoryDal.add_job_to_history(user_id, job_id)