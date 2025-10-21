from project.application.entities.cities import City
from project.domain.core.models.cities import CityModel
from project.utils.data_state import DataFailedMessage, DataState, DataSuccess
from project.utils.db_connection import connection_db


class CityDal:
    @staticmethod
    def get_city_id_by_name(city_name: str) -> DataState[City]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                city = session.query(CityModel).filter(CityModel.name == city_name).first()
                if not city:
                    return DataFailedMessage(f"Город с названием {city_name} не найден")

                return DataSuccess(City.model_validate(city))
            except Exception as e:
                return DataFailedMessage(f"Ошибка при получении города", error=e)