from project.application.entities.cities import City
from project.application.entities.job import Job
from project.application.entities.job_favorite import JobFavorite
from project.domain.cities.cities_bl import CityBl
from project.domain.favorite.favorite_dal import FavoriteJobDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from loguru import logger

class FavoriteJobBL:
    @staticmethod
    def add_job_to_favorite(user_id: int, job_id: int) -> DataState[JobFavorite]:
        return FavoriteJobDal.add_job_to_favorite(user_id, job_id)

    @staticmethod
    def get_list_of_favorites(user_id: int) -> DataState[Job]:
        jobs_state = FavoriteJobDal.get_list_of_favorites(user_id)
        if not jobs_state:
            return jobs_state
        jobs = jobs_state.data
        logger.info(f"Список избранных: {jobs}")
        for job in jobs:
            city_state = CityBl.get_city_name_by_id(job['city_id'])
            if not city_state:
                return DataFailedMessage(error_message=f"Не удалось получить информацию о городе {city_state}")
            city_name = city_state.data
            job['city'] = city_name

        return DataSuccess(jobs)
    @staticmethod
    def delete_job_from_favorites(user_id, job_id) -> DataState:
        return FavoriteJobDal.delete_job_from_favorites(user_id, job_id)




