import psycopg2
from project.config import settings
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class DBConnection:
    @staticmethod
    def connect_db():
        try:
            conn = psycopg2.connect(
                user='postgres',
                password=settings.PASSWORD,
                database=settings.DB_NAME,
                host=settings.HOST_NAME,
                port=settings.PORT
            )
            return conn
        except Exception as ex:
            print("Ошибка подключения: ", ex)
            return None
