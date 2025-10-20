from project.application.entities.cities import City
from project.domain.cities.cities_dal import CityDal
from project.utils.data_state import DataState


class CityBl:
    @staticmethod
    def get_city_id_by_name(city_name: str) -> DataState[City]:
        return CityDal.get_city_id_by_name(city_name)
